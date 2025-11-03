from pydantic import BaseModel, EmailStr
from typing import Optional
from enum import Enum

class UserRole(str, Enum):
    etudiant = "etudiant"
    enseignant = "enseignant"
    admin = "admin"

class UserCreate(BaseModel):
    nom: str
    prenom: str
    nom_utilisateur: str
    email: EmailStr
    mot_de_passe: str

class UserResponse(BaseModel):
    id: int
    nom: str
    prenom: str
    nom_utilisateur: str
    email: EmailStr
    mot_de_passe: str
    role: UserRole

class UserUpdate(BaseModel):
    nom: Optional[str]
    prenom: Optional[str]
    nom_utilisateur: Optional[str]
    email: Optional[EmailStr]
    mot_de_passe: Optional[str]

    class Config:
        from_attributes = True