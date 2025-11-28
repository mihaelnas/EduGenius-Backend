from pydantic import BaseModel, EmailStr , validator
from typing import Optional
from datetime import date
from app.Schema.utilisateurs_schema import UserResponse , UserCreate , UserUpdate

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

class EtudiantUpdate(BaseModel):
    matricule: Optional[str] = None
    date_naissance: Optional[date] = None
    lieu_naissance: Optional[str] = None
    genre: Optional[str] = None
    adresse: Optional[str] = None
    telephone: Optional[str] = None
    niveau_etude: Optional[str] = None
    photo_url: Optional[str] = None
    filiere: Optional[str] = None

class EtudiantDetail(BaseModel):
    user: UserResponse
    matricule: str
    date_naissance: Optional[date]
    lieu_naissance: str
    genre: str
    adresse: Optional[str]
    telephone: Optional[str]
    niveau_etude: Optional[str]
    photo_url: Optional[str]
    filiere: Optional[str]

class AddStudentRequest(BaseModel):
    user: UserUpdate
    etudiant: EtudiantUpdate
class StudentUpdateRequest(BaseModel):
    user: Optional[UserUpdate] = None
    etudiant: Optional[EtudiantUpdate] = None

class EtudiantActivation(BaseModel):
    nom : str
    prenom : str
    matricule: str
    email: EmailStr
    mot_de_passe: str


    class Config:
        from_attributes = True 