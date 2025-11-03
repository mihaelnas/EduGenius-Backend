from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from DB.database import Base
from Model.association_table import enseignant_classe


class Classe(Base):
    __tablename__ = "classes"

    id_classe = Column(Integer, primary_key=True, index=True)
    nom_classe = Column(String, unique=True, index=True, nullable=False)
    niveau = Column(String, nullable=False)
    filiere = Column(String, nullable=False)
    annee_scolaire = Column(String, nullable=False)
    effectif = Column(Integer, nullable=False)

    # Relations
    etudiants = relationship("Etudiant", back_populates="classe")
    enseignants = relationship("Enseignant", secondary=enseignant_classe, back_populates="classe")
    cours = relationship("Cours", back_populates="classe")

# Import à la fin pour éviter les imports circulaires
from Model.etudiant_model import Etudiant
from Model.enseignant_model import Enseignant
from Model.cours_model import Cours

