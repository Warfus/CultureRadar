from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app import models, schemas
from app.auth import get_current_user
from app.database import get_db

router = APIRouter(prefix="/me/participations", tags=["Participations"])


def _serialize(p: models.Participation) -> schemas.ParticipationResponse:
    occ = p.occurrence
    ev = occ.evenement if occ else None
    return schemas.ParticipationResponse(
        id=p.id,
        status=p.status,
        created_at=p.created_at,
        updated_at=p.updated_at,
        occurrence_id=p.occurrence_id,
        occurrence_debut=occ.debut if occ else None,
        occurrence_fin=occ.fin if occ else None,
        occurrence_all_day=occ.all_day if occ else None,
        evenement_id=ev.id if ev else None,
        evenement_titre=ev.titre if ev else None,
        evenement_commune=ev.commune if ev else None,
        evenement_lieu=ev.lieu if ev else None,
        image_url=ev.image_url if ev else None,
    )


@router.get("", response_model=list[schemas.ParticipationResponse])
def list_participations(
    future: bool | None = None,
    db: Session = Depends(get_db),
    current_user: models.Utilisateur = Depends(get_current_user),
):
    query = (
        db.query(models.Participation)
        .options(joinedload(models.Participation.occurrence).joinedload(models.Occurrence.evenement))
        .join(models.Occurrence)
        .filter(models.Participation.utilisateur_id == current_user.id, models.Participation.status == "going")
    )
    if future is True:
        query = query.filter(models.Occurrence.debut >= datetime.now(timezone.utc))
    elif future is False:
        query = query.filter(models.Occurrence.debut < datetime.now(timezone.utc))

    participations = query.order_by(models.Occurrence.debut.asc()).all()
    return [_serialize(p) for p in participations]


@router.post("", response_model=schemas.ParticipationResponse)
def create_participation(
    payload: schemas.ParticipationCreate,
    db: Session = Depends(get_db),
    current_user: models.Utilisateur = Depends(get_current_user),
):
    if not current_user.is_abonne:
        raise HTTPException(status_code=403, detail="Abonnement premium requis pour réserver un événement")

    occurrence = db.query(models.Occurrence).filter(models.Occurrence.id == payload.occurrence_id).first()
    if not occurrence:
        raise HTTPException(status_code=404, detail="Occurrence introuvable")

    existing = (
        db.query(models.Participation)
        .filter(
            models.Participation.utilisateur_id == current_user.id,
            models.Participation.occurrence_id == payload.occurrence_id,
        )
        .first()
    )
    if existing:
        if existing.status == "going":
            raise HTTPException(status_code=409, detail="Vous participez déjà à cet événement")
        existing.status = "going"
        db.commit()
        db.refresh(existing)
        return _serialize(existing)

    participation = models.Participation(
        utilisateur_id=current_user.id, occurrence_id=payload.occurrence_id, status="going"
    )
    db.add(participation)
    db.commit()
    db.refresh(participation)
    return _serialize(participation)


@router.delete("/{participation_id}", status_code=204)
def cancel_participation(
    participation_id: int,
    db: Session = Depends(get_db),
    current_user: models.Utilisateur = Depends(get_current_user),
):
    participation = (
        db.query(models.Participation)
        .filter(models.Participation.id == participation_id, models.Participation.utilisateur_id == current_user.id)
        .first()
    )
    if not participation:
        raise HTTPException(status_code=404, detail="Participation introuvable")

    participation.status = "cancelled"
    db.commit()
