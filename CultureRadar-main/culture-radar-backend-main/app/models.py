from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Float,
    Boolean,
    ForeignKey,
    JSON,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Utilisateur(Base):
    __tablename__ = "utilisateurs"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    mot_de_passe = Column(String, nullable=False)
    role = Column(String, default="user", nullable=False)  # user | organizer | admin

    # Préférences culturelles (héritées de la version initiale)
    musique = Column(Boolean, default=False)
    theatre = Column(Boolean, default=False)
    cinema = Column(Boolean, default=False)
    expositions = Column(Boolean, default=False)

    # Profil utilisé pour les recommandations
    age = Column(Integer, nullable=True)
    preferred_slot = Column(String, nullable=True)  # morning | afternoon | evening | night
    available_days = Column(JSON, nullable=True)  # ["mon", "tue", ...]
    mobility = Column(String, nullable=True)  # walk | bike | car

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Abonnement premium
    is_abonne = Column(Boolean, default=False, nullable=False)
    premium_since = Column(DateTime(timezone=True), nullable=True)

    # Vérification d'email (pas d'envoi d'email réel configuré pour le moment,
    # donc les comptes sont considérés vérifiés par défaut — voir routes/auth_extra.py)
    email_verifie = Column(Boolean, default=True, nullable=False)

    evenements = relationship("Evenement", back_populates="organisateur")
    participations = relationship(
        "Participation", back_populates="utilisateur", cascade="all, delete-orphan"
    )
    ratings = relationship(
        "Rating", back_populates="utilisateur", cascade="all, delete-orphan"
    )


class Evenement(Base):
    __tablename__ = "evenements"

    id = Column(Integer, primary_key=True, index=True)
    titre = Column(String, nullable=False)
    description = Column(String)
    longdescription = Column(String, nullable=True)
    conditions = Column(String, nullable=True)
    image_url = Column(String, nullable=True)

    lieu = Column(String)
    commune = Column(String, nullable=True)
    adresse = Column(String, nullable=True)
    code_postal = Column(String, nullable=True)
    pays = Column(String, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    date = Column(DateTime)  # champ historique, conservé pour compat
    prix = Column(Float, nullable=True)

    keywords = Column(JSON, nullable=True)  # ["musique", "gratuit", ...]
    age_min = Column(Integer, nullable=True)
    age_max = Column(Integer, nullable=True)

    organisateur_id = Column(Integer, ForeignKey("utilisateurs.id"), nullable=True)
    boost_until = Column(DateTime(timezone=True), nullable=True)

    organisateur = relationship("Utilisateur", back_populates="evenements")
    occurrences = relationship(
        "Occurrence", back_populates="evenement", cascade="all, delete-orphan"
    )
    ratings = relationship(
        "Rating", back_populates="evenement", cascade="all, delete-orphan"
    )


class Occurrence(Base):
    __tablename__ = "occurrences"

    id = Column(Integer, primary_key=True, index=True)
    evenement_id = Column(Integer, ForeignKey("evenements.id"), nullable=False)
    debut = Column(DateTime(timezone=True), nullable=False)
    fin = Column(DateTime(timezone=True), nullable=True)
    all_day = Column(Boolean, default=False, nullable=False)

    evenement = relationship("Evenement", back_populates="occurrences")
    participations = relationship(
        "Participation", back_populates="occurrence", cascade="all, delete-orphan"
    )


class Participation(Base):
    __tablename__ = "participations"
    __table_args__ = (
        UniqueConstraint("utilisateur_id", "occurrence_id", name="uq_participation_user_occurrence"),
    )

    id = Column(Integer, primary_key=True, index=True)
    utilisateur_id = Column(Integer, ForeignKey("utilisateurs.id"), nullable=False)
    occurrence_id = Column(Integer, ForeignKey("occurrences.id"), nullable=False)
    status = Column(String, default="going", nullable=False)  # going | cancelled
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    utilisateur = relationship("Utilisateur", back_populates="participations")
    occurrence = relationship("Occurrence", back_populates="participations")


class Rating(Base):
    __tablename__ = "ratings"
    __table_args__ = (
        UniqueConstraint("utilisateur_id", "evenement_id", name="uq_rating_user_event"),
    )

    id = Column(Integer, primary_key=True, index=True)
    utilisateur_id = Column(Integer, ForeignKey("utilisateurs.id"), nullable=False)
    evenement_id = Column(Integer, ForeignKey("evenements.id"), nullable=False)
    rating = Column(Integer, nullable=False)
    commentaire = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    utilisateur = relationship("Utilisateur", back_populates="ratings")
    evenement = relationship("Evenement", back_populates="ratings")


class ContactMessage(Base):
    __tablename__ = "contact_messages"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    subject = Column(String, nullable=True)
    message = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
