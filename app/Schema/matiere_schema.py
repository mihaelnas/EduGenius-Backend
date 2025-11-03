from pydantic import BaseModel
from typing import Optional
from datetime import date
from app.Schema.enseignant_schema import EnseignantResponse

class MatiereCreate(BaseModel):
    nom_matiere: str
    credits: Optional[int]
    semestre: Optional[str]
    photo_url: Optional[str]
    id_enseignant: Optional[int]

class MatiereResponse(BaseModel):
    id_matiere: int
    nom_matiere: str
    credits: Optional[int]
    semestre: Optional[str]
    photo_url: Optional[str]
    enseignant: Optional[EnseignantResponse]

    class Config:
        from_attributes = True