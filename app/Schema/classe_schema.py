from pydantic import BaseModel
from typing import Optional
from datetime import date
from Schema.utilisateurs_schema import UserResponse

class ClasseCreate(BaseModel):
    nom_classe: str
    niveau: str
    filiere: str
    annee_scolaire: str
    effectif: Optional[int]
    id_enseignant: Optional[int]
    

class ClasseResponse(BaseModel):
    id_classe: int
    nom_classe: str
    niveau: str
    filiere: str
    annee_scolaire: str
    effectif: Optional[int]
    enseignant: Optional[UserResponse]

    class Config:
       from_attributes = True