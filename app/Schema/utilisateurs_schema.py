from pydantic import BaseModel, EmailStr
from typing import Optional
from enum import Enum

class UserRole(str, Enum):
    etudiant = "etudiant"
    enseignant = "enseignant"
    admin = "admin"

class UserStatus(str, Enum):
    actif = "actif"
    inactif = "inactif"

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
    status: UserStatus
    role: UserRole

    class Config:
        from_attributes = True 

class UserUpdate(BaseModel):
    nom: Optional[str] = None
    prenom: Optional[str] = None
    nom_utilisateur: Optional[str] = None
    email: Optional[EmailStr] = None
    mot_de_passe: Optional[str] = None

    class Config:
        from_attributes = True 