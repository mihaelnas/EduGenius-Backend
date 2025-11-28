from fastapi import APIRouter, Depends, HTTPException, Query
from app.Sec.Auth import get_current_user
from app.Model.utilisateur_model import User
from sqlalchemy.orm import Session
from app.DB.database import get_db
from app.Model.etudiant_model import Etudiant
from app.Schema.etudiant_schema import EtudiantDetail
from app.Schema.classe_schema import ClasseResponse
from app.Schema.matiere_schema import MatiereResponse
from app.Schema.cours_schema import CoursResponse
from app.Model.planning_model import Evenement
from app.Schema.planning_schema import EvenementResponse
from typing import List, Optional
import datetime


router = APIRouter()

@router.get("/")
def student_dashboard(current_user  = Depends(get_current_user)):
    if current_user.role.value != "etudiant":
        raise HTTPException(status_code=403, detail="Access forbidden")
    return {"message": f"Bienvenue {current_user.nom} !"}

@router.get("/{id_etudiant}", response_model=EtudiantDetail)
async def get_student_details(
    id_etudiant: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role.value != "admin" and current_user.role.value != "etudiant":
        raise HTTPException(status_code=403, detail="Accès réservé à l’administrateur")
    
    etudiant = db.query(Etudiant).filter(Etudiant.id_etudiant == id_etudiant).first()
    if not etudiant:
        raise HTTPException(status_code=404, detail="Étudiant introuvable")
    
    return etudiant

# Obtenir les details de la classe d'un étudiant
@router.get("/{id_etudiant}/classe" , response_model=ClasseResponse)
async def get_student_class_details(
    id_etudiant: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role.value != "admin" and current_user.role.value != "etudiant":
        raise HTTPException(status_code=403, detail="Accès réservé à l’administrateur")
    
    etudiant = db.query(Etudiant).filter(Etudiant.id_etudiant == id_etudiant).first()
    if not etudiant:
        raise HTTPException(status_code=404, detail="Étudiant introuvable")
    
    return etudiant.classe

# Lister les etudiants d'une classe d'une classe assignée à un etudiant
@router.get("/{id_etudiant}/classe/etudiants" , response_model=list[EtudiantDetail])
async def get_students_in_class(
    id_etudiant: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role.value != "admin" and current_user.role.value != "etudiant":
        raise HTTPException(status_code=403, detail="Accès réservé à l’administrateur")
    
    etudiant = db.query(Etudiant).filter(Etudiant.id_etudiant == id_etudiant).first()
    if not etudiant:
        raise HTTPException(status_code=404, detail="Étudiant introuvable")
    
    classe = etudiant.classe
    if not classe:
        raise HTTPException(status_code=404, detail="Classe introuvable pour cet étudiant")
    
    return classe.etudiants

# Lister tous les matières d'un étudiant en fonctions de sa classe a travers les professeurs dans la classe
@router.get("/{id_etudiant}/matieres" , response_model=list[MatiereResponse])
async def get_student_matieres(
    id_etudiant: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role.value != "admin" and current_user.role.value != "etudiant":
        raise HTTPException(status_code=403, detail="Accès réservé à l’administrateur")
    
    etudiant = db.query(Etudiant).filter(Etudiant.id_etudiant == id_etudiant).first()
    if not etudiant:
        raise HTTPException(status_code=404, detail="Étudiant introuvable")
    
    classe = etudiant.classe
    if not classe:
        raise HTTPException(status_code=404, detail="Classe introuvable pour cet étudiant")
    
    matieres = set()
    for professeur in classe.enseignants:
        for matiere in professeur.matieres:
            matieres.add(matiere)
    
    return list(matieres)

# Lister tous les cours d'un étudiant en fonctions de sa classe a travers les professeurs dans la classe
@router.get("/{id_etudiant}/cours", response_model=list[CoursResponse])
async def get_student_cours(
    id_etudiant: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role.value != "admin" and current_user.role.value != "etudiant":
        raise HTTPException(status_code=403, detail="Accès réservé à l’administrateur")
    
    etudiant = db.query(Etudiant).filter(Etudiant.id_etudiant == id_etudiant).first()
    if not etudiant:
        raise HTTPException(status_code=404, detail="Étudiant introuvable")
    
    classe = etudiant.classe
    if not classe:
        raise HTTPException(status_code=404, detail="Classe introuvable pour cet étudiant")
    
    cours = set()
    for professeur in classe.enseignants:
        for matiere in professeur.matieres:
            for cour in matiere.cours:
                cours.add(cour)
    
    return list(cours)

# Obtenir detail d'un cours 
@router.get("/{id_etudiant}/cours/{id_cours}", response_model=CoursResponse)
async def get_course_details_for_student(
    id_etudiant: int,
    id_cours: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role.value != "admin" and current_user.role.value != "etudiant":
        raise HTTPException(status_code=403, detail="Accès réservé à l’administrateur")
    
    etudiant = db.query(Etudiant).filter(Etudiant.id_etudiant == id_etudiant).first()
    if not etudiant:
        raise HTTPException(status_code=404, detail="Étudiant introuvable")
    
    classe = etudiant.classe
    if not classe:
        raise HTTPException(status_code=404, detail="Classe introuvable pour cet étudiant")
    
    for professeur in classe.enseignants:
        for matiere in professeur.matieres:
            for cour in matiere.cours:
                if cour.id_cours == id_cours:
                    return cour
    
    raise HTTPException(status_code=404, detail="Cours introuvable pour cet étudiant")


# Planning étudiant

@router.get("/planning", response_model=List[EvenementResponse])
def student_planning(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role.value != "etudiant":
        raise HTTPException(status_code=403, detail="Accès réservé aux étudiants")

    # récupérer l'objet Etudiant et ses classes (assume relation Etudiant.classes)
    etu = db.query(Etudiant).filter(Etudiant.id_etudiant == current_user.id).first()
    if not etu:
        raise HTTPException(status_code=404, detail="Étudiant introuvable")

    classe_ids = [c.id_classe for c in etu.classes]

    q = db.query(Evenement).filter(Evenement.class_name.in_([c.nom_classe for c in etu.classes]))  # ou filter by id_classe if stored
    # optionally use date filters
    if start_date:
        try:
            sd = datetime.date.fromisoformat(start_date)
        except:
            raise HTTPException(status_code=400, detail="start_date invalide")
        q = q.filter(Evenement.date >= sd)
    if end_date:
        try:
            ed = datetime.date.fromisoformat(end_date)
        except:
            raise HTTPException(status_code=400, detail="end_date invalide")
        q = q.filter(Evenement.date <= ed)

    events = q.order_by(Evenement.date, Evenement.start_time).all()
    return events
