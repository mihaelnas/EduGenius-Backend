from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.DB.database import Base
from app.Model.association_table import enseignant_classe

class Enseignant(Base):
    __tablename__ = "enseignants"

    id_enseignant = Column(Integer, ForeignKey("users.id"), primary_key=True, index=True)
    email_professionnel = Column(String, unique=True, index=True, nullable=False)
    genre = Column(String, nullable=False)
    telephone = Column(String, nullable=False)
    adresse = Column(String, nullable=False)
    specialite = Column(String, nullable=False)
    photo_url = Column(String, nullable=True)
    

    # Relation
    user = relationship("User", back_populates="enseignants", foreign_keys=[id_enseignant])
    matieres = relationship("Matiere", back_populates="enseignants")
    cours = relationship("Cours", back_populates="enseignants")
    classes = relationship("Classe", secondary=enseignant_classe, back_populates="enseignants")
    evenements = relationship("Evenement", back_populates="enseignants")

from app.Model.utilisateur_model import User
from app.Model.matiere_model import Matiere
from app.Model.cours_model import Cours
from app.Model.classe_model import Classe
from app.Model.planning_model import Evenement
