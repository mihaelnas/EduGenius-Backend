from pydantic import BaseModel, EmailStr , validator
from typing import Optional , List
from datetime import date
from app.Schema.utilisateurs_schema import UserResponse , UserCreate , UserUpdate

class EnseignantCreate(BaseModel):
    specialite: Optional[str]
    email_professionnel: Optional[EmailStr]
    genre: Optional[str]
    telephone: Optional[str]
    adresse: Optional[str]
    photo_url: Optional[str]
    id_matiere: Optional[List[int]] = []
    

class AddProfessorRequest(BaseModel):
    user: UserCreate
    enseignant: EnseignantCreate


class EnseignantResponse(BaseModel):
    id_enseignant: int
    specialite: Optional[str]
    email_professionnel: Optional[EmailStr]
    genre: Optional[str]
    telephone: Optional[str]
    adresse: Optional[str]
    photo_url: Optional[str]
    id_matiere: Optional[int]
    user: UserResponse

class EnseignantUpdate(BaseModel):
    specialite: Optional[str] = None
    email_professionnel: Optional[EmailStr] = None
    genre: Optional[str] =  None
    telephone: Optional[str] = None
    adresse: Optional[str] = None
    photo_url: Optional[str] = None

class ProfessorUpdateRequest(BaseModel):
    user: Optional[UserUpdate] = None
    enseignant: Optional[EnseignantUpdate] = None

class EnseignantDetail(BaseModel):
    user: UserResponse
    specialite: Optional[str]
    email_professionnel: Optional[EmailStr]
    genre: Optional[str]
    telephone: Optional[str]
    adresse: Optional[str]
    photo_url: Optional[str]
    
    class Config:
        from_attributes = True 