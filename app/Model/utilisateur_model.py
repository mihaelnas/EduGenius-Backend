from sqlalchemy import Column, Integer, String, Enum
from DB.database import Base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

class UserRole(enum.Enum):
    etudiant = "etudiant"
    enseignant = "enseignant"
    admin = "admin"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, nullable=False)
    prenom = Column(String, nullable=False)
    nom_utilisateur = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    mot_de_passe = Column(String, nullable=False)
    role = Column(Enum(UserRole),default=UserRole.etudiant, nullable=False)
    date_creation = Column(String, default=datetime.utcnow().isoformat(), nullable=False)

    # Relations
    etudiants = relationship("Etudiant", back_populates="user", uselist=False)
    enseignants = relationship("Enseignant", back_populates="user", uselist=False)

from Model.etudiant_model import Etudiant
from Model.enseignant_model import Enseignant