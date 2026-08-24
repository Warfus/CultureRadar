import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app import models
from app.database import engine
from app.routes import admin, auth_extra, evenements, login, organizer, participations, ping, utilisateurs, utils

app = FastAPI(title="CultureRadar API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # à restreindre à l'origine du frontend en production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

models.Base.metadata.create_all(bind=engine)

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

app.include_router(ping.router)
app.include_router(evenements.router)
app.include_router(utilisateurs.router)
app.include_router(login.router)
app.include_router(participations.router)
app.include_router(organizer.router)
app.include_router(admin.router)
app.include_router(utils.router)
app.include_router(auth_extra.router)
