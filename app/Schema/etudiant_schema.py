from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date
from app.Schema.utilisateurs_schema import UserResponse

class EtudiantCreate(BaseModel):
    matricule: str
    date_naissance: Optional[date]
    lieu_naissance: str
    genre: str
    adresse: Optional[str]
    telephone: Optional[str]
    niveau_etude: Optional[str]
    photo_url: Optional[str]
    filiere: Optional[str]

class EtudiantResponse(BaseModel):
    id_etudiant: int
    matricule: str
    date_naissance: Optional[date]
    lieu_naissance: str
    genre: str
    adresse: Optional[str]
    telephone: Optional[str]
    niveau_etude: Optional[str]
    photo_url: Optional[str]
    filiere: Optional[str]
    user: UserResponse

    class Config:
        from_attributes = True