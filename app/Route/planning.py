from fastapi import APIRouter, Depends, HTTPException, status, Query, Response
from sqlalchemy.orm import Session
from typing import Optional, List
from app.DB.database import get_db
from app.Sec.Auth import get_current_user
from app.Model.utilisateur_model import User
from app.Model.planning_model import Evenement, EventType, EventStatus
from app.Schema.planning_schema import EvenementCreate, EvenementResponse, EvenementUpdate
import datetime

router = APIRouter(prefix="/enseignant/planning", tags=["Planning"])

# GET /enseignant/planning?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD
@router.get("", response_model=List[EvenementResponse])
def list_my_events(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # seul rôle enseignant (ou admin éventuellement) peut créer; listage par l'enseignant connecté
    if current_user.role.value not in ["enseignant", "admin", "etudiant"]:
        raise HTTPException(status_code=403, detail="Accès refusé")

    q = db.query(Evenement).filter(Evenement.id_enseignant == current_user.id)

    # si filtres fournis
    if start_date:
        try:
            sd = datetime.date.fromisoformat(start_date)
        except Exception:
            raise HTTPException(status_code=400, detail="start_date invalide")
        q = q.filter(Evenement.date >= sd)
    if end_date:
        try:
            ed = datetime.date.fromisoformat(end_date)
        except Exception:
            raise HTTPException(status_code=400, detail="end_date invalide")
        q = q.filter(Evenement.date <= ed)

    events = q.order_by(Evenement.date, Evenement.start_time).all()
    return events

# POST /enseignant/planning
@router.post("", response_model=EvenementResponse, status_code=status.HTTP_201_CREATED)
def create_event(
    payload: EvenementCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role.value != "enseignant":
        raise HTTPException(status_code=403, detail="Accès réservé aux enseignants")

    # validations simples
    if payload.startTime >= payload.endTime:
        raise HTTPException(status_code=400, detail="startTime doit être avant endTime")

    new_ev = Evenement(
        date=payload.date,
        start_time=payload.startTime,
        end_time=payload.endTime,
        subject=payload.subject,
        class_name=payload.class_name,
        type=payload.type,
        status=payload.status,
        conference_link=str(payload.conferenceLink) if payload.conferenceLink else None,
        id_enseignant=current_user.id
    )
    db.add(new_ev)
    db.commit()
    db.refresh(new_ev)
    return new_ev

# PUT /enseignant/planning/{id_evenement}
@router.put("/{id_evenement}", response_model=EvenementResponse)
def update_event(
    id_evenement: int,
    payload: EvenementUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    ev = db.query(Evenement).filter(Evenement.id_evenement == id_evenement).first()
    if not ev:
        raise HTTPException(status_code=404, detail="Événement introuvable")

    # only owner teacher or admin
    if current_user.role.value != "admin" and ev.id_enseignant != current_user.id:
        raise HTTPException(status_code=403, detail="Accès refusé")

    # apply updates
    if payload.date is not None:
        ev.date = payload.date
    if payload.startTime is not None:
        ev.start_time = payload.startTime
    if payload.endTime is not None:
        ev.end_time = payload.endTime
    if payload.subject is not None:
        ev.subject = payload.subject
    if payload.class_name is not None:
        ev.class_name = payload.class_name
    if payload.type is not None:
        ev.type = payload.type
    if payload.status is not None:
        ev.status = payload.status
    if payload.conferenceLink is not None:
        ev.conference_link = str(payload.conferenceLink)
    if payload.notes is not None:
        ev.notes = payload.notes

    # validation time
    if ev.start_time >= ev.end_time:
        raise HTTPException(status_code=400, detail="startTime doit être avant endTime")

    db.commit()
    db.refresh(ev)
    return ev

# DELETE /enseignant/planning/{id_evenement}
@router.delete("/{id_evenement}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(
    id_evenement: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    ev = db.query(Evenement).filter(Evenement.id_evenement == id_evenement).first()
    if not ev:
        raise HTTPException(status_code=404, detail="Événement introuvable")

    if current_user.role.value != "admin" and ev.id_enseignant != current_user.id:
        raise HTTPException(status_code=403, detail="Accès refusé")

    db.delete(ev)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# Affichage des événements pour un étudiant
@router.get("/etudiant/{id_etudiant}", response_model=List[EvenementResponse])
def list_events_for_student(
    id_etudiant: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role.value not in ["enseignant", "admin", "etudiant"]:
        raise HTTPException(status_code=403, detail="Accès refusé")

    # vérifier que l'étudiant existe
    from Model.etudiant_model import Etudiant
    etudiant = db.query(Etudiant).filter(Etudiant.id_etudiant == id_etudiant).first()
    if not etudiant:
        raise HTTPException(status_code=404, detail="Étudiant introuvable")

    # récupérer les événements liés à la classe de l'étudiant
    events = db.query(Evenement).filter(Evenement.class_name == etudiant.classe.nom_classe).order_by(Evenement.date, Evenement.start_time).all()
    return events