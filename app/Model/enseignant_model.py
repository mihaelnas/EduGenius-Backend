from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from DB.database import Base
from Model.association_table import enseignant_classe

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
    classe = relationship("Classe", secondary=enseignant_classe, back_populates="enseignants")

from Model.utilisateur_model import User
from Model.matiere_model import Matiere
from Model.cours_model import Cours
from Model.classe_model import Classe
