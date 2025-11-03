from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from DB.database import Base

class Matiere(Base):
    __tablename__ = "matieres"

    id_matiere = Column(Integer, primary_key=True, index=True)
    nom_matiere = Column(String(50), nullable=False)
    credit = Column(Integer)
    semestre = Column(String(10))
    id_enseignant = Column(Integer, ForeignKey("enseignants.id_enseignant"), nullable=True)
    phto_url = Column(String, nullable=True)

    # Relations
    enseignants = relationship("Enseignant", back_populates="matieres", foreign_keys=[id_enseignant])
    cours = relationship("Cours", back_populates="matieres")

from Model.enseignant_model import Enseignant
from Model.cours_model import Cours
