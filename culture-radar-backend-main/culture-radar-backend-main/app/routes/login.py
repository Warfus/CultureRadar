from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.auth import create_access_token, verify_mot_de_passe
from app.database import get_db

router = APIRouter(tags=["Login"])


@router.post("/login")
def login(payload: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.Utilisateur).filter(models.Utilisateur.email == payload.email).first()

    # Même message pour email inconnu et mot de passe incorrect : on évite de
    # révéler si l'adresse email existe dans la base.
    if not user or not verify_mot_de_passe(payload.mot_de_passe, user.mot_de_passe):
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")

    if not user.email_verifie:
        raise HTTPException(status_code=403, detail="Email non vérifié")

    token = create_access_token({"user_id": user.id, "role": user.role})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user_id": user.id,
        "user": schemas.UtilisateurResponse.model_validate(user),
    }
