# Schema/evenement_schema.py
from pydantic import BaseModel, Field, HttpUrl
from typing import Optional
import datetime
from enum import Enum

class EventStatus(str, Enum):
    planifie = "planifié"
    reporte = "reporté"
    annule = "annulé"
    effectue = "effectué"

class EventType(str, Enum):
    en_salle = "en-salle"
    en_ligne = "en-ligne"

class EvenementBase(BaseModel):
    date: datetime.date
    startTime: datetime.time = Field(..., alias="startTime")
    endTime: datetime.time = Field(..., alias="endTime")
    subject: str
    class_name: str = Field(..., alias="class")
    type: EventType
    status: EventStatus
    conferenceLink: Optional[HttpUrl] = Field(None, alias="conferenceLink")
    notes: Optional[str] = None

class EvenementCreate(EvenementBase):
    pass

class EvenementUpdate(BaseModel):
    date: Optional[datetime.date] = None
    startTime: Optional[datetime.time] = Field(None, alias="startTime")
    endTime: Optional[datetime.time] = Field(None, alias="endTime")
    subject: Optional[str] = None
    class_name: Optional[str] = Field(None, alias="class")
    type: Optional[EventType] = None
    status: Optional[EventStatus] = None
    conferenceLink: Optional[HttpUrl] = Field(None, alias="conferenceLink")
    notes: Optional[str] = None

class EvenementResponse(EvenementBase):
    id_evenement: int
    id_enseignant: int
    id_cours: Optional[int] = None

    class Config:
        from_attributes = True
        validate_by_name = True
