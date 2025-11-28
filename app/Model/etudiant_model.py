from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.DB.database import Base

class Etudiant(Base):
    __tablename__ = "etudiants"

    id_etudiant = Column(Integer, ForeignKey("users.id"), primary_key=True, index=True)
    matricule = Column(String(10), unique=True, index=True, nullable=False)
    date_naissance = Column(String, nullable=False)
    lieu_naissance = Column(String, nullable=False)
    genre = Column(String, nullable=False)
    telephone = Column(String, nullable=False)
    adresse = Column(String, nullable=False)
    niveau_etude = Column(String, nullable=False)
    filiere = Column(String, nullable=False)
    photo_url = Column(String, nullable=True)
    id_classe = Column(Integer, ForeignKey("classes.id_classe", ondelete="SET NULL"), nullable=True , )
    
    # Relation
    user = relationship("User", back_populates="etudiants", foreign_keys=[id_etudiant])
    classes = relationship("Classe", back_populates="etudiants", foreign_keys=[id_classe])

from app.Model.utilisateur_model import User
from app.Model.classe_model import Classe