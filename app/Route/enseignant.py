from fastapi import APIRouter, Depends, HTTPException
from app.Sec.Auth import get_current_user
from sqlalchemy.orm import Session
from app.DB.database import get_db
from app.Model.utilisateur_model import User
from app.Model.enseignant_model import Enseignant
from app.Schema.enseignant_schema import EnseignantDetail
from app.Schema.classe_schema import ClasseResponse
from app.Schema.etudiant_schema import EtudiantDetail
from app.Schema.matiere_schema import MatiereResponse
from app.Schema.cours_schema import CoursResponse


router = APIRouter()



@router.get("/")
def enseignant_dashboard(current_user = Depends(get_current_user)):
    if current_user.role.value != "enseignant":
        raise HTTPException(status_code=403, detail="Access forbidden")
    return {"message": f"Bienvenue, enseignant {current_user.nom} !"}


# Details d'un professeur
@router.get("/{prof_id}", response_model=EnseignantDetail)
async def get_professor_details(
    prof_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role.value != "admin" and current_user.role.value != "enseignant":
        raise HTTPException(status_code=403, detail="Accès réservé à l’administrateur")

    prof = db.query(Enseignant).filter(Enseignant.id_enseignant == prof_id).first()
    if not prof:
        raise HTTPException(status_code=404, detail="Professeur introuvable")

    return prof

# liste des classes assignées à un enseignant
@router.get("/{id_enseignant}/classes", response_model=list[ClasseResponse])
async def get_assigned_classes(
    id_enseignant: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role.value != "admin" and current_user.role.value != "enseignant":
        raise HTTPException(status_code=403, detail="Accès réservé à l’administrateur")

    enseignant = db.query(Enseignant).filter(Enseignant.id_enseignant == id_enseignant).first()
    if not enseignant:
        raise HTTPException(status_code=404, detail="Enseignant introuvable")

    if enseignant.classes :
        return enseignant.classes
    else:
        raise HTTPException(status_code=404 , detail="Aucune classe  ")

# Lister les etudiants d'une classe assignée à un enseignant
@router.get("/{id_enseignant}/classes/{id_classe}/etudiants", response_model=list[EtudiantDetail])
async def get_students_in_class(
    id_enseignant: int,
    id_classe: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role.value != "admin" and current_user.role.value != "enseignant":
        raise HTTPException(status_code=403, detail="Accès réservé à l’administrateur")

    enseignant = db.query(Enseignant).filter(Enseignant.id_enseignant == id_enseignant).first()
    if not enseignant:
        raise HTTPException(status_code=404, detail="Enseignant introuvable")

    classe = next((c for c in enseignant.classes if c.id_classe == id_classe), None)
    if not classe:
        raise HTTPException(status_code=404, detail="Classe introuvable pour cet enseignant")

    return classe.etudiants


# Obtenir detail d'une classe assignée à un enseignant
@router.get("/{id_enseignant}/classes/{id_classe}", response_model=ClasseResponse)
async def get_class_details(
    id_enseignant: int,
    id_classe: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role.value != "admin" and current_user.role.value != "enseignant":
        raise HTTPException(status_code=403, detail="Accès réservé à l’administrateur")

    enseignant = db.query(Enseignant).filter(Enseignant.id_enseignant == id_enseignant).first()
    if not enseignant:
        raise HTTPException(status_code=404, detail="Enseignant introuvable")

    classe = next((c for c in enseignant.classes if c.id_classe == id_classe), None)
    if not classe:
        raise HTTPException(status_code=404, detail="Classe introuvable pour cet enseignant")

    return classe


# liste des matieres assignées à un enseignant
@router.get("/{id_enseignant}/matieres" , response_model=list[MatiereResponse])
async def get_assigned_matieres(
    id_enseignant: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role.value != "admin" and current_user.role.value != "enseignant":
        raise HTTPException(status_code=403, detail="Accès réservé à l’administrateur")

    enseignant = db.query(Enseignant).filter(Enseignant.id_enseignant == id_enseignant).first()
    if not enseignant:
        raise HTTPException(status_code=404, detail="Enseignant introuvable")

    return enseignant.matieres


# liste des cours assignées à un enseignant pour une matiere 
@router.get("/{id_enseignant}/matieres/{id_matiere}/cours" , response_model=list[CoursResponse])
async def get_assigned_cours(
    id_enseignant: int,
    id_matiere: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role.value != "admin" and current_user.role.value != "enseignant":
        raise HTTPException(status_code=403, detail="Accès réservé à l’administrateur")

    enseignant = db.query(Enseignant).filter(Enseignant.id_enseignant == id_enseignant).first()
    if not enseignant:
        raise HTTPException(status_code=404, detail="Enseignant introuvable")

    matiere = next((m for m in enseignant.matieres if m.id_matiere == id_matiere), None)
    if not matiere:
        raise HTTPException(status_code=404, detail="Matiere introuvable pour cet enseignant")

    return matiere.cours
