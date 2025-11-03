from sqlalchemy import Column, Integer, String, Text, Enum, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from DB.database import Base
import enum

class TypeCours(enum.Enum):
    presentiel = "présentiel"
    en_ligne = "en_ligne"
    mixte = "mixte"

class Cours(Base):
    __tablename__ = "cours"

    id_cours = Column(Integer, primary_key=True, index=True)
    titre = Column(String(150), nullable=False)
    contenu = Column(Text)
    type_cours = Column(Enum(TypeCours), default=TypeCours.en_ligne)
    date_publication = Column(DateTime, default=datetime.utcnow)
    duree_estimee = Column(Integer)
    id_enseignant = Column(Integer, ForeignKey("enseignants.id_enseignant"))
    id_matiere = Column(Integer, ForeignKey("matieres.id_matiere"))
    id_classe = Column(Integer, ForeignKey("classes.id_classe"))

    # Relations
    enseignants = relationship("Enseignant", back_populates="cours", foreign_keys=[id_enseignant])
    matieres = relationship("Matiere", back_populates="cours", foreign_keys=[id_matiere])
    classe = relationship("Classe", back_populates="cours", foreign_keys=[id_classe])

from Model.enseignant_model import Enseignant
from Model.matiere_model import Matiere
from Model.classe_model import Classe