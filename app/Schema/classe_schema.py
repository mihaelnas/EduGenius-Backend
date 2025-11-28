from pydantic import BaseModel
from typing import Optional, List
from datetime import date
from app.Schema.utilisateurs_schema import UserResponse
from app.Schema.enseignant_schema import EnseignantDetail
from app.Schema.etudiant_schema import EtudiantDetail

class ClasseCreate(BaseModel):
    nom_classe: str
    niveau: str
    filiere: str
    annee_scolaire: str
    effectif: Optional[int]
    id_enseignant: Optional[List[int]] = []
    

class ClasseResponse(BaseModel):
    id_classe: int
    nom_classe: str
    niveau: str
    filiere: str
    annee_scolaire: str
    effectif: Optional[int]
    enseignants: Optional[List[EnseignantDetail]] = []
    etudiants: Optional[List[EtudiantDetail]] = []

    class Config:
       from_attributes = True