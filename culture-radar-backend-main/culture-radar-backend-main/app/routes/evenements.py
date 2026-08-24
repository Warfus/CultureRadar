from datetime import datetime, timedelta, timezone
from math import atan2, cos, radians, sin, sqrt
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app import models, schemas
from app.auth import get_current_user, require_organizer
from app.database import get_db

router = APIRouter(prefix="/evenements", tags=["Evenements"])

PREFERENCE_KEYWORDS = {
    "musique": "musique",
    "theatre": "théâtre",
    "cinema": "cinéma",
    "expositions": "exposition",
}

SLOT_HOURS = {
    "morning": range(6, 12),
    "afternoon": range(12, 18),
    "evening": range(18, 22),
    "night": list(range(22, 24)) + list(range(0, 6)),
}

WEEKDAY_CODES = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]


def _now():
    return datetime.now(timezone.utc)


def _aware(dt: Optional[datetime]) -> Optional[datetime]:
    """Certains backends (ex. SQLite en tests) renvoient des datetimes naïfs
    même pour une colonne DateTime(timezone=True) ; on les traite comme UTC."""
    if dt is not None and dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    return r * 2 * atan2(sqrt(a), sqrt(1 - a))


def serialize_event(ev: models.Evenement) -> dict:
    ratings = ev.ratings or []
    count = len(ratings)
    average = round(sum(r.rating for r in ratings) / count, 2) if count else None

    data = schemas.EvenementResponse.model_validate(ev).model_dump()
    data["owner_id"] = ev.organisateur_id
    data["rating_average"] = average
    data["rating_count"] = count
    return data


def _earliest_occurrence(ev: models.Evenement, only_future: bool = True) -> Optional[datetime]:
    now = _now()
    candidates = [_aware(o.debut) for o in ev.occurrences if not only_future or _aware(o.debut) >= now]
    if not candidates and only_future:
        candidates = [_aware(o.debut) for o in ev.occurrences]
    return min(candidates) if candidates else None


def _base_query(db: Session):
    return db.query(models.Evenement).options(
        joinedload(models.Evenement.occurrences), joinedload(models.Evenement.ratings)
    )


def _apply_sql_filters(
    query,
    q: Optional[str],
    city: Optional[str],
    future_only: bool,
    date_from: Optional[datetime],
    date_to: Optional[datetime],
    hour_from: Optional[int],
    hour_to: Optional[int],
    age_min_lte: Optional[int],
    age_max_gte: Optional[int],
):
    if q:
        like = f"%{q}%"
        query = query.filter(
            (models.Evenement.titre.ilike(like)) | (models.Evenement.description.ilike(like))
        )
    if city:
        query = query.filter(models.Evenement.commune.ilike(f"%{city}%"))
    if age_min_lte is not None:
        query = query.filter(
            (models.Evenement.age_min.is_(None)) | (models.Evenement.age_min <= age_min_lte)
        )
    if age_max_gte is not None:
        query = query.filter(
            (models.Evenement.age_max.is_(None)) | (models.Evenement.age_max >= age_max_gte)
        )

    needs_occurrence_join = future_only or date_from or date_to or hour_from is not None or hour_to is not None
    if needs_occurrence_join:
        query = query.join(models.Occurrence)
        if future_only:
            query = query.filter(models.Occurrence.debut >= _now())
        if date_from:
            query = query.filter(models.Occurrence.debut >= date_from)
        if date_to:
            query = query.filter(models.Occurrence.debut <= date_to)
        if hour_from is not None:
            query = query.filter(func.extract("hour", models.Occurrence.debut) >= hour_from)
        if hour_to is not None:
            query = query.filter(func.extract("hour", models.Occurrence.debut) <= hour_to)
        query = query.distinct()

    return query


def _apply_python_filters(
    events: List[models.Evenement],
    lat: Optional[float],
    lon: Optional[float],
    radius_km: Optional[float],
    kw_any: List[str],
    kw_none: List[str],
):
    result = []
    kw_any_lower = {k.lower() for k in kw_any}
    kw_none_lower = {k.lower() for k in kw_none}

    for ev in events:
        if lat is not None and lon is not None and radius_km is not None:
            if ev.latitude is None or ev.longitude is None:
                continue
            if _haversine_km(lat, lon, ev.latitude, ev.longitude) > radius_km:
                continue

        ev_keywords = {k.lower() for k in (ev.keywords or [])}
        if kw_any_lower and not (ev_keywords & kw_any_lower):
            continue
        if kw_none_lower and (ev_keywords & kw_none_lower):
            continue

        result.append(ev)

    return result


@router.get("/", response_model=None)
def read_evenements(
    db: Session = Depends(get_db),
    page: Optional[int] = Query(None, ge=1),
    per_page: Optional[int] = Query(None, ge=1, le=200),
    limit: Optional[int] = Query(None, ge=1, le=200),
    offset: Optional[int] = Query(None, ge=0),
    future_only: bool = False,
    order: Optional[str] = None,
    q: Optional[str] = None,
    city: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    hour_from: Optional[int] = None,
    hour_to: Optional[int] = None,
    lat: Optional[float] = None,
    lon: Optional[float] = None,
    radius_km: Optional[float] = None,
    age_min_lte: Optional[int] = None,
    age_max_gte: Optional[int] = None,
    kw_any: List[str] = Query(default_factory=list),
    kw_none: List[str] = Query(default_factory=list),
):
    query = _apply_sql_filters(
        _base_query(db), q, city, future_only, date_from, date_to, hour_from, hour_to, age_min_lte, age_max_gte
    )
    events = _apply_python_filters(query.all(), lat, lon, radius_km, kw_any, kw_none)

    if order == "date_asc":
        events.sort(key=lambda e: _earliest_occurrence(e) or datetime.max.replace(tzinfo=timezone.utc))

    if limit is not None:
        start = offset or 0
        events = events[start : start + limit]
    elif page is not None and per_page is not None:
        start = (page - 1) * per_page
        events = events[start : start + per_page]

    return [serialize_event(ev) for ev in events]


@router.get("/home", response_model=None)
def read_home(
    db: Session = Depends(get_db),
    limit: int = Query(20, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    query = _apply_sql_filters(_base_query(db), None, None, True, None, None, None, None, None, None)
    events = query.all()
    events.sort(
        key=lambda e: (
            0 if (_aware(e.boost_until) and _aware(e.boost_until) >= _now()) else 1,
            _earliest_occurrence(e) or datetime.max.replace(tzinfo=timezone.utc),
        )
    )
    events = events[offset : offset + limit]
    return [serialize_event(ev) for ev in events]


@router.get("/reco", response_model=None)
def read_reco(
    db: Session = Depends(get_db),
    current_user: models.Utilisateur = Depends(get_current_user),
    limit: int = Query(20, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    query = _apply_sql_filters(_base_query(db), None, None, True, None, None, None, None, None, None)
    events = query.all()

    liked_keywords = {
        PREFERENCE_KEYWORDS[flag]
        for flag in PREFERENCE_KEYWORDS
        if getattr(current_user, flag, False)
    }
    slot_hours = SLOT_HOURS.get(current_user.preferred_slot or "", None)
    available_days = set(current_user.available_days or [])

    def score(ev: models.Evenement) -> int:
        s = 0
        ev_keywords = {k.lower() for k in (ev.keywords or [])}
        if liked_keywords and (ev_keywords & {k.lower() for k in liked_keywords}):
            s += 2
        for occ in ev.occurrences:
            if slot_hours and occ.debut.hour in slot_hours:
                s += 1
            if available_days and WEEKDAY_CODES[occ.debut.weekday()] in available_days:
                s += 1
        if _aware(ev.boost_until) and _aware(ev.boost_until) >= _now():
            s += 1
        return s

    events.sort(
        key=lambda e: (
            -score(e),
            _earliest_occurrence(e) or datetime.max.replace(tzinfo=timezone.utc),
        )
    )
    events = events[offset : offset + limit]
    return [serialize_event(ev) for ev in events]


@router.post("/", response_model=None)
def create_evenement(
    evenement: schemas.EvenementCreate,
    db: Session = Depends(get_db),
    current_user: models.Utilisateur = Depends(require_organizer),
):
    data = evenement.model_dump(exclude={"occurrences"})
    db_event = models.Evenement(**data, organisateur_id=current_user.id)
    db.add(db_event)
    db.flush()

    for occ in evenement.occurrences:
        db.add(models.Occurrence(evenement_id=db_event.id, **occ.model_dump()))

    db.commit()
    db.refresh(db_event)
    return serialize_event(db_event)


@router.get("/{evenement_id}", response_model=None)
def read_evenement(evenement_id: int, db: Session = Depends(get_db)):
    ev = _base_query(db).filter(models.Evenement.id == evenement_id).first()
    if not ev:
        raise HTTPException(status_code=404, detail="Événement introuvable")
    return serialize_event(ev)


@router.post("/{evenement_id}/promote/boost30")
def boost_event(
    evenement_id: int,
    db: Session = Depends(get_db),
    current_user: models.Utilisateur = Depends(require_organizer),
):
    ev = db.query(models.Evenement).filter(models.Evenement.id == evenement_id).first()
    if not ev:
        raise HTTPException(status_code=404, detail="Événement introuvable")
    if ev.organisateur_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Cet événement ne vous appartient pas")

    ev.boost_until = _now() + timedelta(days=30)
    db.commit()
    return {"boost_until": ev.boost_until}


# ---------------------------------------------------------------------------
# Notes et avis
# ---------------------------------------------------------------------------

@router.get("/{evenement_id}/ratings", response_model=List[schemas.RatingPublic])
def list_ratings(
    evenement_id: int,
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
):
    ratings = (
        db.query(models.Rating)
        .options(joinedload(models.Rating.utilisateur))
        .filter(models.Rating.evenement_id == evenement_id)
        .order_by(models.Rating.created_at.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )
    return [
        schemas.RatingPublic(
            id=r.id,
            user_id=r.utilisateur_id,
            user_nom=r.utilisateur.nom if r.utilisateur else None,
            rating=r.rating,
            commentaire=r.commentaire,
            created_at=r.created_at,
        )
        for r in ratings
    ]


@router.get("/{evenement_id}/ratings/avg", response_model=schemas.RatingAverage)
def ratings_average(evenement_id: int, db: Session = Depends(get_db)):
    ratings = db.query(models.Rating).filter(models.Rating.evenement_id == evenement_id).all()
    count = len(ratings)
    average = round(sum(r.rating for r in ratings) / count, 2) if count else None
    return schemas.RatingAverage(average=average, count=count)


@router.get("/{evenement_id}/ratings/me", response_model=schemas.RatingMine)
def my_rating(
    evenement_id: int,
    db: Session = Depends(get_db),
    current_user: models.Utilisateur = Depends(get_current_user),
):
    r = (
        db.query(models.Rating)
        .filter(models.Rating.evenement_id == evenement_id, models.Rating.utilisateur_id == current_user.id)
        .first()
    )
    if not r:
        return schemas.RatingMine(rating=None, commentaire=None)
    return schemas.RatingMine(rating=r.rating, commentaire=r.commentaire)


@router.put("/{evenement_id}/ratings", response_model=schemas.RatingAverage)
def upsert_rating(
    evenement_id: int,
    payload: schemas.RatingIn,
    db: Session = Depends(get_db),
    current_user: models.Utilisateur = Depends(get_current_user),
):
    ev = db.query(models.Evenement).filter(models.Evenement.id == evenement_id).first()
    if not ev:
        raise HTTPException(status_code=404, detail="Événement introuvable")

    attended_past = (
        db.query(models.Participation)
        .join(models.Occurrence)
        .filter(
            models.Participation.utilisateur_id == current_user.id,
            models.Participation.status == "going",
            models.Occurrence.evenement_id == evenement_id,
            models.Occurrence.debut < _now(),
        )
        .first()
    )
    if not attended_past:
        raise HTTPException(
            status_code=403,
            detail="Vous ne pouvez noter que les événements passés auxquels vous avez participé",
        )

    r = (
        db.query(models.Rating)
        .filter(models.Rating.evenement_id == evenement_id, models.Rating.utilisateur_id == current_user.id)
        .first()
    )
    if r:
        r.rating = payload.rating
        r.commentaire = payload.commentaire
    else:
        r = models.Rating(
            evenement_id=evenement_id,
            utilisateur_id=current_user.id,
            rating=payload.rating,
            commentaire=payload.commentaire,
        )
        db.add(r)

    db.commit()

    ratings = db.query(models.Rating).filter(models.Rating.evenement_id == evenement_id).all()
    count = len(ratings)
    average = round(sum(x.rating for x in ratings) / count, 2) if count else None
    return schemas.RatingAverage(average=average, count=count)
