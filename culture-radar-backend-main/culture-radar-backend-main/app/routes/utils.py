import os
import uuid

import requests
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db

router = APIRouter(tags=["Utils"])

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
MAX_UPLOAD_SIZE = 5 * 1024 * 1024  # 5 Mo


@router.get("/utils/geocode", response_model=schemas.GeocodeResponse)
def geocode(q: str):
    if not q or not q.strip():
        raise HTTPException(status_code=422, detail="Le paramètre 'q' est requis")

    try:
        response = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q": q, "format": "json", "limit": 1},
            headers={"User-Agent": "CultureRadar/1.0 (contact: contact@cultureradar.local)"},
            timeout=5,
        )
        response.raise_for_status()
        results = response.json()
    except requests.RequestException:
        raise HTTPException(status_code=502, detail="Service de géocodage indisponible")

    if not results:
        raise HTTPException(status_code=404, detail="Adresse introuvable")

    return schemas.GeocodeResponse(lat=float(results[0]["lat"]), lon=float(results[0]["lon"]))


@router.post("/utils/contact", status_code=201)
def contact(payload: schemas.ContactForm, db: Session = Depends(get_db)):
    if payload.website:
        # Champ honeypot rempli : probablement un bot, on répond sans rien faire.
        return {"status": "ok"}

    message = models.ContactMessage(
        name=payload.name,
        email=payload.email,
        subject=payload.subject,
        message=payload.message,
    )
    db.add(message)
    db.commit()
    return {"status": "ok"}


@router.post("/upload/image")
async def upload_image(file: UploadFile = File(...)):
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=415, detail="Type de fichier non autorisé")

    content = await file.read()
    if len(content) > MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=413, detail="Fichier trop volumineux (5 Mo max)")

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    extension = os.path.splitext(file.filename or "")[1].lower()
    if extension not in (".jpg", ".jpeg", ".png", ".webp", ".gif"):
        extension = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp", "image/gif": ".gif"}.get(
            file.content_type, ".jpg"
        )

    filename = f"{uuid.uuid4().hex}{extension}"
    filepath = os.path.join(UPLOAD_DIR, filename)
    with open(filepath, "wb") as f:
        f.write(content)

    return {"url": f"/uploads/{filename}"}
