"""Remplit la base avec des événements de démonstration À VENIR (Île-de-France).

Usage (depuis le dossier du backend, avec DATABASE_URL défini dans .env) :
    python seed_demo.py

- Crée (si absents) un compte utilisateur et un compte organisateur de test.
- Supprime les anciens événements de démonstration (mot-clé "demo") puis en recrée 60,
  datés à partir d'aujourd'hui sur 6 mois, chacun avec 2 à 4 séances réservables.
- Peut être relancé à tout moment pour « rafraîchir » les dates.
"""
import random
from datetime import datetime, timedelta, timezone

from app.database import SessionLocal, engine
from app import models
from app.auth import hash_mot_de_passe

models.Base.metadata.create_all(bind=engine)
random.seed(42)

MDP_TEST = "CultureRadar2025!"

LIEUX = [
    ("La Marbrerie", "Montreuil", "21 rue Alexis Lepère", "93100", 48.8566, 2.4390),
    ("Théâtre Berthelot", "Montreuil", "6 rue Marcelin Berthelot", "93100", 48.8590, 2.4410),
    ("Médiathèque Robert-Desnos", "Montreuil", "14 boulevard Rouget de Lisle", "93100", 48.8613, 2.4430),
    ("Le Comptoir", "Fontenay-sous-Bois", "26 rue Gérard Philipe", "94120", 48.8510, 2.4760),
    ("Maison des arts de Créteil", "Créteil", "Place Salvador Allende", "94000", 48.7905, 2.4520),
    ("MAC VAL", "Vitry-sur-Seine", "Place de la Libération", "94400", 48.7920, 2.3880),
    ("Le Hasard Ludique", "Paris", "128 avenue de Saint-Ouen", "75018", 48.8960, 2.3270),
    ("La Bellevilloise", "Paris", "19-21 rue Boyer", "75020", 48.8680, 2.3920),
    ("Point Éphémère", "Paris", "200 quai de Valmy", "75010", 48.8810, 2.3680),
    ("Le Studio Théâtre de Stains", "Stains", "19 rue Carnot", "93240", 48.9500, 2.3830),
    ("Les Instants Chavirés", "Montreuil", "7 rue Richard Lenoir", "93100", 48.8540, 2.4300),
    ("Parc des Beaumonts", "Montreuil", "Rue Paul Doumer", "93100", 48.8650, 2.4580),
]

TYPES = [
    ("Concert jazz manouche", ["musique", "concert", "jazz"], 10, (18, 99)),
    ("Scène ouverte rap", ["musique", "concert", "rap"], 5, (16, 99)),
    ("Exposition street art", ["exposition", "art urbain", "gratuit"], 0, (0, 99)),
    ("Atelier BD pour enfants", ["atelier", "famille", "enfants", "gratuit"], 0, (6, 10)),
    ("Comédie d'improvisation", ["théâtre", "humour"], 12, (12, 99)),
    ("Conte musical jeune public", ["spectacle", "famille", "enfants"], 5, (4, 8)),
    ("Ciné-débat documentaire", ["cinéma", "débat"], 4, (14, 99)),
    ("Bal folk en plein air", ["musique", "danse", "plein air", "gratuit"], 0, (0, 99)),
    ("Visite d'ateliers d'artistes", ["exposition", "visite", "gratuit"], 0, (0, 99)),
    ("Concert de musique classique", ["musique", "concert", "classique"], 15, (8, 99)),
]

def get_or_create_user(db, email, nom, role):
    u = db.query(models.Utilisateur).filter_by(email=email).first()
    if not u:
        u = models.Utilisateur(nom=nom, email=email, mot_de_passe=hash_mot_de_passe(MDP_TEST),
                               role=role, email_verifie=True, musique=True, expositions=True, age=29)
        db.add(u)
        db.flush()
    return u

def main():
    db = SessionLocal()
    get_or_create_user(db, "test@cultureradar.fr", "Utilisateur Test", "user")
    orga = get_or_create_user(db, "orga@cultureradar.fr", "Organisateur Test", "organizer")

    anciens = [e for e in db.query(models.Evenement).all() if "demo" in (e.keywords or [])]
    for e in anciens:
        db.delete(e)
    db.flush()

    now = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
    n = 0
    for i in range(60):
        titre, kws, prix, (amin, amax) = TYPES[i % len(TYPES)]
        lieu, ville, adresse, cp, lat, lon = LIEUX[i % len(LIEUX)]
        jour = now + timedelta(days=2 + (i * 3) % 180)
        heure = random.choice([11, 14, 15, 18, 19, 20])
        ev = models.Evenement(
            titre=f"{titre} – {ville}",
            description=f"{titre} à {lieu} ({ville}). Événement de démonstration pour tester la recherche et la réservation.",
            longdescription="Événement fictif créé pour la démonstration du projet étudiant CultureRadar : aucune réservation réelle.",
            conditions="Gratuit" if prix == 0 else f"{prix} € sur place",
            image_url=None,
            lieu=lieu, commune=ville, adresse=adresse, code_postal=cp, pays="France",
            latitude=lat + random.uniform(-0.002, 0.002), longitude=lon + random.uniform(-0.002, 0.002),
            date=jour.replace(hour=heure),
            prix=float(prix),
            keywords=kws + ["demo"],
            age_min=amin, age_max=amax,
            organisateur_id=orga.id if i % 3 == 0 else None,
            boost_until=(now + timedelta(days=30)) if i % 10 == 0 else None,
        )
        db.add(ev)
        db.flush()
        for s in range(random.randint(2, 4)):
            debut = (jour + timedelta(days=7 * s)).replace(hour=heure)
            db.add(models.Occurrence(evenement_id=ev.id, debut=debut, fin=debut + timedelta(hours=2), all_day=False))
        n += 1
    db.commit()
    db.close()
    print(f"{len(anciens)} anciens événements de démo supprimés, {n} événements à venir créés.")
    print(f"Comptes de test : test@cultureradar.fr / orga@cultureradar.fr (mot de passe : {MDP_TEST})")

if __name__ == "__main__":
    main()
