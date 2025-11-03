from pydantic import BaseModel, EmailStr
from typing import Optional , List
from datetime import date
from Schema.utilisateurs_schema import UserResponse

class EnseignantCreate(BaseModel):
    specialite: Optional[str]
    email_professionnel: Optional[EmailStr]
    genre: Optional[str]
    telephone: Optional[str]
    adresse: Optional[str]
    photo_url: Optional[str]
    id_matiere: Optional[List[int]] = []
    

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
    specialite: Optional[str]
    email_professionnel: Optional[EmailStr]
    genre: Optional[str]
    telephone: Optional[str]
    adresse: Optional[str]
    photo_url: Optional[str]

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