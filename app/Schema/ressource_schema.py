# Schema/ressource_schema.py
from pydantic import BaseModel, HttpUrl
from typing import Optional
import datetime

class RessourceCreate(BaseModel):
    titre: str
    type_resource: str
    url: HttpUrl

class RessourceResponse(BaseModel):
    id_ressource: int
    titre: str
    type_resource: str
    url: HttpUrl
    id_cours: int
    id_enseignant: int
    created_at: datetime.datetime

    class Config:
        from_attrbutes = True
