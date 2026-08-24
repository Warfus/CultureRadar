from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app import models, schemas
from app.auth import require_organizer
from app.database import get_db
from app.routes.evenements import serialize_event

router = APIRouter(prefix="/organizer", tags=["Organizer"])


@router.get("/events", response_model=None)
def list_my_events(
    db: Session = Depends(get_db),
    current_user: models.Utilisateur = Depends(require_organizer),
):
    query = db.query(models.Evenement).options(
        joinedload(models.Evenement.occurrences), joinedload(models.Evenement.ratings)
    )
    if current_user.role != "admin":
        query = query.filter(models.Evenement.organisateur_id == current_user.id)
    events = query.all()
    return [serialize_event(ev) for ev in events]


@router.post("/events", response_model=None)
def create_my_event(
    payload: schemas.EvenementCreate,
    db: Session = Depends(get_db),
    current_user: models.Utilisateur = Depends(require_organizer),
):
    data = payload.model_dump(exclude={"occurrences"})
    db_event = models.Evenement(**data, organisateur_id=current_user.id)
    db.add(db_event)
    db.flush()

    for occ in payload.occurrences:
        db.add(models.Occurrence(evenement_id=db_event.id, **occ.model_dump()))

    db.commit()
    db.refresh(db_event)
    return serialize_event(db_event)


@router.delete("/events/{evenement_id}", status_code=204)
def delete_my_event(
    evenement_id: int,
    db: Session = Depends(get_db),
    current_user: models.Utilisateur = Depends(require_organizer),
):
    ev = db.query(models.Evenement).filter(models.Evenement.id == evenement_id).first()
    if not ev:
        raise HTTPException(status_code=404, detail="Événement introuvable")
    if ev.organisateur_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Cet événement ne vous appartient pas")

    db.delete(ev)
    db.commit()
