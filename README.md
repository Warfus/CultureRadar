# CultureRadar

Plateforme de recommandation culturelle personnalisée et locale — projet étudiant
(Bachelor IA & Data, Agence Insight Nova). Ce dépôt regroupe le backend (API) et
le frontend (site web).

## Structure du projet

```
CultureRadar-main/
├── culture-radar-backend-main/     → API FastAPI (Python)
└── Culture_radar_frontend_angular-main/  → Site web Angular (TypeScript)
```

## Prérequis

- **Python 3.10 ou plus récent** (`python --version` pour vérifier)
- **Node.js et npm** (`node --version` et `npm --version` pour vérifier)
- **Git**

## Lancer le backend en local

Dans un terminal :

```bash
cd culture-radar-backend-main/culture-radar-backend-main

# Créer l'environnement virtuel Python (une seule fois)
python -m venv venv

# L'activer (à refaire à chaque nouveau terminal)
# Windows :
.\venv\Scripts\activate
# macOS/Linux :
source venv/bin/activate

# Installer les dépendances (une seule fois, ou après une mise à jour de requirements.txt)
pip install -r requirements.txt
```

Créer un fichier `.env` à la racine de ce dossier (non fourni dans le dépôt, il
contient des secrets) avec ce contenu minimum :

```
DATABASE_URL=sqlite:///./test_local.db
SECRET_KEY=change-moi-en-une-valeur-longue-et-aleatoire
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

(`DATABASE_URL` ci-dessus utilise SQLite pour un test rapide sans rien installer
d'autre. Pour une vraie base PostgreSQL, remplacer par
`postgresql://utilisateur:motdepasse@hote:5432/nom_de_la_base`.)

Puis lancer le serveur :

```bash
uvicorn app.main:app --reload
```

Le serveur tourne sur `http://127.0.0.1:8000`. La documentation interactive de
l'API (Swagger) est disponible sur `http://127.0.0.1:8000/docs`.

## Lancer le frontend en local

Dans un **second** terminal (laisser le backend tourner dans le premier) :

```bash
cd Culture_radar_frontend_angular-main/Culture_radar_angular-main

npm install
npm start
```

Le site est disponible sur `http://localhost:4200`. En développement
(`npm start` / `ng serve`), le frontend appelle automatiquement le backend en
local (`http://127.0.0.1:8000`) grâce à `src/environments/environment.ts`.

## Déploiement en production

`src/environments/environment.prod.ts` contient l'URL du backend déployé
(Render). C'est ce fichier qui est utilisé automatiquement quand on build avec :

```bash
ng build --configuration production
```

Vérifier que cette URL est à jour avant tout déploiement réel.

## Export de la base de données

Un export SQL de démonstration (schéma complet + données représentatives) est
disponible séparément dans le dossier des livrables du projet
(`Export_SQL_CultureRadar.sql`), généré en exécutant le schéma réel de
l'application sur une base PostgreSQL de test.

## Notes

- Le fichier `.env` du backend n'est **jamais** commité (voir `.gitignore`) car
  il contient des secrets (clé JWT, identifiants de base de données).
- La vérification d'adresse e-mail à l'inscription est actuellement désactivée
  par défaut (aucun service d'envoi d'e-mail n'est configuré) — les comptes
  sont considérés vérifiés dès la création.
