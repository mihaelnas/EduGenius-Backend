from pydantic import BaseModel 
from typing import Optional
from enum import Enum
from datetime import datetime
from Schema.classe_schema import ClasseResponse


class TypeCours(str, Enum):
    presentiel = "présentiel"
    en_ligne = "en_ligne"
    mixte = "mixte"

class CoursCreate(BaseModel):
    titre: str
    contenu: Optional[str]
    type_cours: Optional[TypeCours] = TypeCours.en_ligne
    duree_estimee: Optional[int]  # durée en minutes
    id_enseignant: Optional[int]
    id_matiere: Optional[int]
    id_classe: Optional[int]

class CoursResponse(BaseModel):
    id_cours: int
    titre: str
    contenu: Optional[str]
    type_cours: TypeCours
    date_publication: datetime
    duree_estimee: Optional[int]
    id_enseignant: Optional[int]
    id_matiere: Optional[int]
    id_classe: Optional[int]
    
    
    classe: Optional[ClasseResponse]

    class Config:
        from_attributes = True

    