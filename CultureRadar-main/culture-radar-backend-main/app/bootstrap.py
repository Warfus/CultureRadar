"""Remplissage automatique d'une base VIDE au démarrage de l'API.

Utile quand la base PostgreSQL gratuite de Render expire et doit être recréée :
dès que l'API démarre sur la nouvelle base (vide), elle crée
- les comptes de test (test@cultureradar.fr, orga@cultureradar.fr) avec SEED_PASSWORD,
- le compte administrateur du jury (admin@cultureradar.fr) avec ADMIN_JURY_PASSWORD,
- 60 événements de démonstration à venir.
Rien n'est fait si la base contient déjà des utilisateurs. Aucun mot de passe n'est écrit
dans le code : ils sont lus dans les variables d'environnement.
"""
import logging
import os

from app import models
from app.database import SessionLocal

log = logging.getLogger("bootstrap")


def bootstrap_si_base_vide() -> None:
    seed_pwd = os.getenv("SEED_PASSWORD")
    admin_pwd = os.getenv("ADMIN_JURY_PASSWORD")
    db = SessionLocal()
    try:
        if db.query(models.Utilisateur).first() is not None:
            return
        import seed_demo  # noqa: import tardif (script à la racine du backend)

        if admin_pwd:
            seed_demo.get_or_create_user(db, "admin@cultureradar.fr", "Administrateur Jury", "admin", admin_pwd)
        if seed_pwd:
            seed_demo.MDP_TEST = seed_pwd
            _, n = seed_demo.seed(db)
            log.warning("Base vide : comptes de test et %s événements de démonstration créés.", n)
        db.commit()
    except Exception as exc:  # ne jamais empêcher l'API de démarrer
        db.rollback()
        log.warning("Remplissage automatique ignoré : %s", exc)
    finally:
        db.close()
