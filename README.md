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

- **Python 3.12** — recommandé fortement (`python --version` pour vérifier). Les
  versions plus récentes (3.13+) posent parfois problème à l'installation de
  certaines dépendances compilées (`bcrypt`, `psycopg2-binary`, `cryptography`)
  faute de paquet précompilé disponible pour la nouvelle version. Si tu as déjà
  une autre version installée, tu peux installer 3.12 en plus sans la
  désinstaller (voir "Plusieurs versions de Python" plus bas).
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

### Plusieurs versions de Python sur la même machine

Si `python --version` affiche une version différente de 3.12 et que tu ne veux
pas désinstaller celle déjà présente, installe Python 3.12 en plus (depuis
python.org, "Add python.exe to PATH" coché comme d'habitude). Ensuite, utilise
le lanceur `py` avec le numéro de version pour cibler spécifiquement 3.12,
plutôt que `python` :

```bash
py -3.12 -m venv venv
```

Le reste des commandes (`pip install`, `uvicorn`, etc.) fonctionne normalement
une fois le `venv` créé et activé, peu importe la version utilisée pour le
créer.

### Configurer le fichier `.env`

Le fichier `.env` contient des secrets et n'est **pas** fourni dans le dépôt
(voir `.gitignore`) — il faut le créer toi-même, une seule fois, à la racine
de ce dossier backend (`culture-radar-backend-main/culture-radar-backend-main`,
au même niveau que `requirements.txt`).

Le plus fiable est de le créer depuis le terminal, dans ce dossier (créer un
fichier nommé exactement `.env` depuis l'explorateur Windows est piégeux : il
ajoute souvent `.txt` à la fin sans le montrer) :

```bash
notepad .env
```

Windows va demander si tu veux créer un nouveau fichier — accepte. Notepad
s'ouvre avec un fichier vide : colle ce contenu dedans, puis enregistre
(Ctrl+S) et ferme :

```
DATABASE_URL=sqlite:///./test_local.db
SECRET_KEY=change-moi-en-une-valeur-longue-et-aleatoire
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

(`DATABASE_URL` ci-dessus utilise SQLite pour un test rapide sans rien installer
d'autre. Pour une vraie base PostgreSQL, remplacer par
`postgresql://utilisateur:motdepasse@hote:5432/nom_de_la_base`.)

Vérifier que le fichier existe bien sous ce nom exact (pas `.env.txt`) :

```bash
dir .env*
```

Doit afficher uniquement `.env`. Si tu vois `.env.txt`, renomme-le :

```bash
ren .env.txt .env
```

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

Le site est déployé sur Render :

- Frontend : https://ias-b3-1-paris-g3.fr
- Backend (API) : https://api.ias-b3-1-paris-g3.fr/docs

`src/environments/environment.prod.ts` contient l'URL du backend déployé
(Render). C'est ce fichier qui est utilisé automatiquement quand on build avec :

```bash
ng build --configuration production
```

Vérifier que cette URL est à jour avant tout déploiement réel.

## Export de la base de données

Un export SQL réel (schéma complet + données) de la base de données de
production est disponible dans le dossier des livrables du projet
(`Export_SQL_CultureRadar.sql`), généré via `pg_dump` sur la base PostgreSQL
Render en production, et vérifié par restauration complète.

## Notes

- Le fichier `.env` du backend n'est **jamais** commité (voir `.gitignore`) car
  il contient des secrets (clé JWT, identifiants de base de données).
- La vérification d'adresse e-mail à l'inscription est actuellement désactivée
  par défaut (aucun service d'envoi d'e-mail n'est configuré) — les comptes
  sont considérés vérifiés dès la création.
