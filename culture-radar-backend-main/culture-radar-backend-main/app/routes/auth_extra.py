from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models
from app.auth import verify_token
from app.database import get_db

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.get("/verify-email")
def verify_email(token: str, db: Session = Depends(get_db)):
    payload = verify_token(token)
    if not payload or payload.get("purpose") != "verify_email":
        raise HTTPException(status_code=400, detail="Lien de vérification invalide ou expiré")

    user = db.query(models.Utilisateur).filter(models.Utilisateur.id == payload.get("user_id")).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")

    user.email_verifie = True
    db.commit()
    return {"status": "ok"}
