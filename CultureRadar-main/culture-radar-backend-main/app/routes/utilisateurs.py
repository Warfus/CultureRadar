from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.auth import get_current_user, hash_mot_de_passe, require_admin
from app.database import get_db

router = APIRouter(prefix="/utilisateurs", tags=["Utilisateurs"])


@router.post("/", response_model=schemas.UtilisateurResponse)
def create_utilisateur(utilisateur: schemas.UtilisateurCreate, db: Session = Depends(get_db)):
    db_utilisateur = db.query(models.Utilisateur).filter(models.Utilisateur.email == utilisateur.email).first()
    if db_utilisateur:
        raise HTTPException(status_code=409, detail="Email déjà utilisé")

    utilisateur_dict = utilisateur.model_dump()
    utilisateur_dict["mot_de_passe"] = hash_mot_de_passe(utilisateur_dict["mot_de_passe"])

    new_user = models.Utilisateur(**utilisateur_dict)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post("/organisateurs", response_model=schemas.UtilisateurResponse, status_code=201)
def create_organisateur(payload: schemas.OrganisateurCreate, db: Session = Depends(get_db)):
    """Inscription dédiée aux organisateurs : on ne leur demande pas leurs goûts ni
    leurs disponibilités (inutiles pour eux), mais les informations de leur structure."""
    email = payload.email.strip().lower()
    if db.query(models.Utilisateur).filter(models.Utilisateur.email == email).first():
        raise HTTPException(status_code=409, detail="Email déjà utilisé")
    if not any(c.isupper() for c in payload.mot_de_passe):
        raise HTTPException(status_code=422, detail="Le mot de passe doit contenir une majuscule")

    new_user = models.Utilisateur(
        nom=payload.nom.strip(),
        email=email,
        mot_de_passe=hash_mot_de_passe(payload.mot_de_passe),
        role="organizer",
    )
    db.add(new_user)
    db.flush()
    db.add(models.ProfilOrganisateur(utilisateur_id=new_user.id, **payload.structure.model_dump()))
    db.commit()
    db.refresh(new_user)
    return new_user


@router.get("/me/organisateur", response_model=schemas.ProfilOrganisateurResponse)
def read_my_organizer_profile(current_user: models.Utilisateur = Depends(get_current_user)):
    if not current_user.profil_organisateur:
        raise HTTPException(status_code=404, detail="Aucun profil organisateur")
    return current_user.profil_organisateur


@router.get("/me", response_model=schemas.UtilisateurResponse)
def read_me(current_user: models.Utilisateur = Depends(get_current_user)):
    return current_user


@router.put("/me", response_model=schemas.UtilisateurResponse)
def update_me(
    updates: schemas.UtilisateurUpdate,
    current_user: models.Utilisateur = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    update_data = updates.model_dump(exclude_unset=True)

    if "email" in update_data and update_data["email"] != current_user.email:
        existing = db.query(models.Utilisateur).filter(models.Utilisateur.email == update_data["email"]).first()
        if existing:
            raise HTTPException(status_code=409, detail="Email déjà utilisé")

    for key, value in update_data.items():
        setattr(current_user, key, value)

    db.commit()
    db.refresh(current_user)
    return current_user


@router.get("/me/subscription", response_model=schemas.SubscriptionStatus)
def get_subscription(current_user: models.Utilisateur = Depends(get_current_user)):
    return schemas.SubscriptionStatus(
        is_active=current_user.is_abonne,
        premium_since=current_user.premium_since,
    )


@router.post("/me/subscribe", response_model=schemas.SubscriptionStatus)
def subscribe(
    current_user: models.Utilisateur = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not current_user.is_abonne:
        current_user.is_abonne = True
        current_user.premium_since = datetime.now(timezone.utc)
        db.commit()
        db.refresh(current_user)
    return schemas.SubscriptionStatus(
        is_active=current_user.is_abonne,
        premium_since=current_user.premium_since,
    )


@router.post("/me/unsubscribe", response_model=schemas.SubscriptionStatus)
def unsubscribe(
    current_user: models.Utilisateur = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    current_user.is_abonne = False
    db.commit()
    db.refresh(current_user)
    return schemas.SubscriptionStatus(
        is_active=current_user.is_abonne,
        premium_since=current_user.premium_since,
    )


@router.get("/", response_model=list[schemas.UtilisateurResponse])
def get_utilisateurs(db: Session = Depends(get_db), _admin: models.Utilisateur = Depends(require_admin)):
    return db.query(models.Utilisateur).all()


@router.patch("/{id}", response_model=schemas.UtilisateurResponse)
def update_utilisateur(
    id: int,
    updates: schemas.UtilisateurUpdate,
    db: Session = Depends(get_db),
    _admin: models.Utilisateur = Depends(require_admin),
):
    utilisateur = db.query(models.Utilisateur).filter(models.Utilisateur.id == id).first()

    if not utilisateur:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")

    update_data = updates.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(utilisateur, key, value)

    db.commit()
    db.refresh(utilisateur)
    return utilisateur
