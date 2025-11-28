from sqlalchemy import Column, Integer, Date, Time, String, Enum, ForeignKey, Text
from sqlalchemy.orm import relationship
import enum
from app.DB.database import Base

class EventStatus(enum.Enum):
    planifie = "planifié"
    reporte = "reporté"
    annule = "annulé"
    effectue = "effectué"

class EventType(enum.Enum):
    en_salle = "en-salle"
    en_ligne = "en-ligne"

class Evenement(Base):
    __tablename__ = "evenements"

    id_evenement = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    subject = Column(String(255), nullable=False)     # nom de la matière (pour affichage rapide)
    class_name = Column(String(255), nullable=False)  # nom de la classe (pour affichage)
    type = Column(Enum(EventType), nullable=False, default=EventType.en_salle)
    status = Column(Enum(EventStatus), nullable=False, default=EventStatus.planifie)
    conference_link = Column(String(1024), nullable=True)
    notes = Column(Text, nullable=True)
    


    # relations
    id_enseignant = Column(Integer, ForeignKey("enseignants.id_enseignant"), nullable=False)  # ou enseignants.id_enseignant selon ton schéma
    id_cours = Column(Integer, ForeignKey("cours.id_cours"), nullable=True)

    enseignants = relationship("Enseignant", back_populates="evenements")  # adapte si ton model User est ailleurs
    cours = relationship("Cours", back_populates="evenements")

from app.Model.utilisateur_model import User
from app.Model.cours_model import Cours