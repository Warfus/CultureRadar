import csv
import io
import zipfile
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy import func
from sqlalchemy.orm import Session

from app import models
from app.auth import require_admin
from app.database import get_db

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/stats/overview")
def stats_overview(db: Session = Depends(get_db), _admin: models.Utilisateur = Depends(require_admin)):
    now = datetime.now(timezone.utc)
    total_users = db.query(func.count(models.Utilisateur.id)).scalar()
    total_events = db.query(func.count(models.Evenement.id)).scalar()
    total_participations = (
        db.query(func.count(models.Participation.id)).filter(models.Participation.status == "going").scalar()
    )
    total_ratings = db.query(func.count(models.Rating.id)).scalar()
    avg_rating = db.query(func.avg(models.Rating.rating)).scalar()
    premium_users = db.query(func.count(models.Utilisateur.id)).filter(models.Utilisateur.is_abonne.is_(True)).scalar()
    upcoming_events = (
        db.query(func.count(func.distinct(models.Occurrence.evenement_id)))
        .filter(models.Occurrence.debut >= now)
        .scalar()
    )
    organizers = db.query(func.count(models.Utilisateur.id)).filter(models.Utilisateur.role == "organizer").scalar()

    return {
        "total_users": total_users or 0,
        "total_events": total_events or 0,
        "total_participations": total_participations or 0,
        "total_ratings": total_ratings or 0,
        "average_rating": round(avg_rating, 2) if avg_rating is not None else None,
        "premium_users": premium_users or 0,
        "upcoming_events": upcoming_events or 0,
        "organizers": organizers or 0,
    }


@router.get("/stats/time-series")
def stats_time_series(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    _admin: models.Utilisateur = Depends(require_admin),
):
    now = datetime.now(timezone.utc)
    start = now - timedelta(days=days - 1)

    signups = (
        db.query(func.date(models.Utilisateur.created_at).label("day"), func.count(models.Utilisateur.id))
        .filter(models.Utilisateur.created_at >= start)
        .group_by("day")
        .all()
    )
    participations = (
        db.query(func.date(models.Participation.created_at).label("day"), func.count(models.Participation.id))
        .filter(models.Participation.created_at >= start)
        .group_by("day")
        .all()
    )

    signups_map = {str(day): count for day, count in signups}
    participations_map = {str(day): count for day, count in participations}

    series = []
    for i in range(days):
        day = (start + timedelta(days=i)).date()
        key = str(day)
        series.append(
            {
                "date": key,
                "signups": signups_map.get(key, 0),
                "participations": participations_map.get(key, 0),
            }
        )

    return {"days": days, "series": series}


@router.get("/top/events")
def top_events(
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    _admin: models.Utilisateur = Depends(require_admin),
):
    rows = (
        db.query(
            models.Evenement.id,
            models.Evenement.titre,
            func.count(func.distinct(models.Participation.id)).label("participations_count"),
            func.avg(models.Rating.rating).label("avg_rating"),
        )
        .outerjoin(models.Occurrence, models.Occurrence.evenement_id == models.Evenement.id)
        .outerjoin(
            models.Participation,
            (models.Participation.occurrence_id == models.Occurrence.id)
            & (models.Participation.status == "going"),
        )
        .outerjoin(models.Rating, models.Rating.evenement_id == models.Evenement.id)
        .group_by(models.Evenement.id, models.Evenement.titre)
        .order_by(func.count(func.distinct(models.Participation.id)).desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "id": r.id,
            "titre": r.titre,
            "participations_count": r.participations_count or 0,
            "average_rating": round(r.avg_rating, 2) if r.avg_rating is not None else None,
        }
        for r in rows
    ]


@router.get("/content/quality")
def content_quality(db: Session = Depends(get_db), _admin: models.Utilisateur = Depends(require_admin)):
    total = db.query(func.count(models.Evenement.id)).scalar() or 0
    missing_description = (
        db.query(func.count(models.Evenement.id))
        .filter((models.Evenement.description.is_(None)) | (models.Evenement.description == ""))
        .scalar()
    )
    missing_image = (
        db.query(func.count(models.Evenement.id))
        .filter((models.Evenement.image_url.is_(None)) | (models.Evenement.image_url == ""))
        .scalar()
    )
    without_occurrence = (
        db.query(func.count(models.Evenement.id))
        .filter(~models.Evenement.occurrences.any())
        .scalar()
    )

    return {
        "total_events": total,
        "missing_description": missing_description or 0,
        "missing_image": missing_image or 0,
        "without_occurrence": without_occurrence or 0,
    }


@router.get("/users")
def list_users(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=200),
    q: Optional[str] = None,
    db: Session = Depends(get_db),
    _admin: models.Utilisateur = Depends(require_admin),
):
    query = db.query(models.Utilisateur)
    if q:
        like = f"%{q}%"
        query = query.filter((models.Utilisateur.nom.ilike(like)) | (models.Utilisateur.email.ilike(like)))

    users = query.order_by(models.Utilisateur.id.asc()).offset((page - 1) * per_page).limit(per_page).all()
    return [
        {
            "id": u.id,
            "nom": u.nom,
            "email": u.email,
            "role": u.role,
            "is_abonne": u.is_abonne,
            "created_at": u.created_at,
        }
        for u in users
    ]


@router.delete("/users/{user_id}", status_code=204)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin: models.Utilisateur = Depends(require_admin),
):
    if user_id == admin.id:
        raise HTTPException(status_code=400, detail="Impossible de supprimer votre propre compte")

    user = db.query(models.Utilisateur).filter(models.Utilisateur.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")

    db.delete(user)
    db.commit()


@router.get("/events")
def list_events(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=200),
    q: Optional[str] = None,
    db: Session = Depends(get_db),
    _admin: models.Utilisateur = Depends(require_admin),
):
    query = db.query(models.Evenement)
    if q:
        query = query.filter(models.Evenement.titre.ilike(f"%{q}%"))

    events = query.order_by(models.Evenement.id.asc()).offset((page - 1) * per_page).limit(per_page).all()
    return [
        {
            "id": e.id,
            "titre": e.titre,
            "commune": e.commune,
            "organisateur_id": e.organisateur_id,
        }
        for e in events
    ]


@router.delete("/events/{evenement_id}", status_code=204)
def delete_event(
    evenement_id: int,
    db: Session = Depends(get_db),
    _admin: models.Utilisateur = Depends(require_admin),
):
    ev = db.query(models.Evenement).filter(models.Evenement.id == evenement_id).first()
    if not ev:
        raise HTTPException(status_code=404, detail="Événement introuvable")

    db.delete(ev)
    db.commit()


TABLE_MODELS = {
    "utilisateurs": models.Utilisateur,
    "evenements": models.Evenement,
    "occurrences": models.Occurrence,
    "participations": models.Participation,
    "ratings": models.Rating,
}


@router.get("/export.zip")
def export_zip(
    tables: Optional[str] = None,
    db: Session = Depends(get_db),
    _admin: models.Utilisateur = Depends(require_admin),
):
    requested = [t.strip() for t in tables.split(",")] if tables else list(TABLE_MODELS.keys())
    unknown = [t for t in requested if t not in TABLE_MODELS]
    if unknown:
        raise HTTPException(status_code=400, detail=f"Table(s) inconnue(s) : {', '.join(unknown)}")

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for table_name in requested:
            model = TABLE_MODELS[table_name]
            rows = db.query(model).all()
            columns = [c.name for c in model.__table__.columns]

            csv_buffer = io.StringIO()
            writer = csv.writer(csv_buffer)
            writer.writerow(columns)
            for row in rows:
                writer.writerow([getattr(row, col) for col in columns])

            zf.writestr(f"{table_name}.csv", csv_buffer.getvalue())

    buffer.seek(0)
    return Response(
        content=buffer.read(),
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=cultureradar_export.zip"},
    )
