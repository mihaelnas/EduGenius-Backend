# Model/ressource_model.py
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.DB.database import Base
import enum

class ResourceType(enum.Enum):
    pdf = "pdf"
    video = "video"
    link = "link"
    other = "other"

class Ressource(Base):
    __tablename__ = "ressources"

    id_ressource = Column(Integer, primary_key=True, index=True)
    titre = Column(String(255), nullable=False)
    type_resource = Column(Enum(ResourceType), nullable=False)
    url = Column(String(2000), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    id_cours = Column(Integer, ForeignKey("cours.id_cours"), nullable=False)
    id_enseignant = Column(Integer, ForeignKey("users.id"), nullable=False)  # créateur

    cours = relationship("Cours", backref="ressources")
    enseignant = relationship("User", backref="ressources")

from app.Model.cours_model import Cours
from app.Model.utilisateur_model import User