from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


# ---------------------------------------------------------------------------
# Utilisateurs
# ---------------------------------------------------------------------------

class UtilisateurBase(BaseModel):
    nom: str
    email: str
    musique: Optional[bool] = False
    theatre: Optional[bool] = False
    cinema: Optional[bool] = False
    expositions: Optional[bool] = False
    age: Optional[int] = None
    preferred_slot: Optional[str] = None
    available_days: Optional[List[str]] = None
    mobility: Optional[str] = None


class UtilisateurCreate(UtilisateurBase):
    mot_de_passe: str


class UtilisateurResponse(UtilisateurBase):
    id: int
    role: str
    created_at: Optional[datetime] = None
    is_abonne: bool = False
    premium_since: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class UtilisateurUpdate(BaseModel):
    nom: Optional[str] = None
    email: Optional[str] = None
    musique: Optional[bool] = None
    theatre: Optional[bool] = None
    cinema: Optional[bool] = None
    expositions: Optional[bool] = None
    age: Optional[int] = None
    preferred_slot: Optional[str] = None
    available_days: Optional[List[str]] = None
    mobility: Optional[str] = None


class LoginRequest(BaseModel):
    email: str
    mot_de_passe: str


class SubscriptionStatus(BaseModel):
    is_active: bool
    premium_since: Optional[datetime] = None


# ---------------------------------------------------------------------------
# Occurrences
# ---------------------------------------------------------------------------

class OccurrenceBase(BaseModel):
    debut: datetime
    fin: Optional[datetime] = None
    all_day: Optional[bool] = False


class OccurrenceCreate(OccurrenceBase):
    pass


class OccurrenceResponse(OccurrenceBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Evenements
# ---------------------------------------------------------------------------

class EvenementBase(BaseModel):
    titre: str
    description: Optional[str] = None
    longdescription: Optional[str] = None
    conditions: Optional[str] = None
    image_url: Optional[str] = None
    lieu: Optional[str] = None
    commune: Optional[str] = None
    adresse: Optional[str] = None
    code_postal: Optional[str] = None
    pays: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    keywords: Optional[List[str]] = None
    age_min: Optional[int] = None
    age_max: Optional[int] = None
    prix: Optional[float] = None


class EvenementCreate(EvenementBase):
    occurrences: List[OccurrenceCreate] = Field(default_factory=list)


class EvenementResponse(EvenementBase):
    id: int
    date: Optional[datetime] = None
    owner_id: Optional[int] = None
    boost_until: Optional[datetime] = None
    occurrences: List[OccurrenceResponse] = Field(default_factory=list)
    rating_average: Optional[float] = None
    rating_count: int = 0

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Participations
# ---------------------------------------------------------------------------

class ParticipationCreate(BaseModel):
    occurrence_id: int


class ParticipationResponse(BaseModel):
    id: int
    status: str
    created_at: datetime
    updated_at: datetime
    occurrence_id: int
    occurrence_debut: Optional[datetime] = None
    occurrence_fin: Optional[datetime] = None
    occurrence_all_day: Optional[bool] = None
    evenement_id: int
    evenement_titre: Optional[str] = None
    evenement_commune: Optional[str] = None
    evenement_lieu: Optional[str] = None
    image_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Ratings
# ---------------------------------------------------------------------------

class RatingIn(BaseModel):
    rating: int = Field(ge=1, le=5)
    commentaire: Optional[str] = None


class RatingMine(BaseModel):
    rating: Optional[int] = None
    commentaire: Optional[str] = None


class RatingPublic(BaseModel):
    id: int
    user_id: int
    user_nom: Optional[str] = None
    rating: int
    commentaire: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RatingAverage(BaseModel):
    average: Optional[float] = None
    count: int = 0


# ---------------------------------------------------------------------------
# Divers / utilitaires
# ---------------------------------------------------------------------------

class ContactForm(BaseModel):
    name: str
    email: str
    subject: Optional[str] = None
    message: str
    website: Optional[str] = ""  # honeypot anti-spam, doit rester vide


class GeocodeResponse(BaseModel):
    lat: float
    lon: float
