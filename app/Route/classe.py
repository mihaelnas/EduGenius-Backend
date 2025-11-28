from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from app.DB.database import get_db
from app.Model.classe_model import Classe
from app.Schema.classe_schema import ClasseCreate, ClasseResponse
from app.Schema.utilisateurs_schema import UserResponse
from app.Schema.etudiant_schema import EtudiantDetail
from app.Sec.Auth import get_current_user
from app.Model.classe_model import Classe
from app.Model.etudiant_model import Etudiant 
from app.Model.enseignant_model import Enseignant
from app.Schema.classe_schema import ClasseCreate , ClasseResponse
from app.Model.utilisateur_model import User

router = APIRouter(prefix="/dashboard/admin/classes", tags=["Classes"])



# ✅ Créer une classe
@router.post("/creer_classe", response_model=ClasseResponse, status_code=status.HTTP_201_CREATED)
async def create_class(
    classe: ClasseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Action réservée à l’administrateur")

    db_classe = db.query(Classe).filter(Classe.nom_classe == classe.nom_classe).first()
    if db_classe:
        raise HTTPException(status_code=400, detail="Une classe avec ce nom existe déjà")

    new_classe = Classe(
        nom_classe=classe.nom_classe,
        niveau=classe.niveau,
        filiere=classe.filiere,
        annee_scolaire=classe.annee_scolaire,
        effectif=classe.effectif or 0
    )

    if classe.id_enseignant:
        enseignants = db.query(Enseignant).filter(Enseignant.id_enseignant.in_(classe.id_enseignant)).all()
        if not enseignants:
            raise HTTPException(status_code=404, detail="Enseignant introuvable")
        new_classe.enseignants = enseignants 
    else:
        new_classe.enseignants = []

    db.add(new_classe)
    db.commit()
    db.refresh(new_classe)
    return new_classe

# ✅ Lister toutes les classes
@router.get("/", response_model=list[ClasseResponse])
async def list_classes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Accès réservé à l’administrateur")

    classes = db.query(Classe).all()
    return classes

# ✅ Obtenir les détails d'une classe
@router.get("/classe/{classe_id}", response_model=ClasseResponse)
async def get_class_details(
    classe_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Accès réservé à l’administrateur")

    classe = db.query(Classe).filter(Classe.id_classe == classe_id).first()
    if not classe:
        raise HTTPException(status_code=404, detail="Classe introuvable")

    return classe

# ✅ Supprimer une classe
@router.delete("/supprimer_classe/{classe_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_class(
    classe_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Action réservée à l’administrateur")

    classe = db.query(Classe).filter(Classe.id_classe == classe_id).first()
    if not classe:
        raise HTTPException(status_code=404, detail="Classe introuvable")

    db.delete(classe)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ✅ Mettre à jour une classe
@router.put("/modifier_classe/{classe_id}", response_model=ClasseResponse)
async def update_class(
    classe_id: int,
    classe_update: ClasseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Action réservée à l’administrateur")

    classe = db.query(Classe).filter(Classe.id_classe == classe_id).first()
    if not classe:
        raise HTTPException(status_code=404, detail="Classe introuvable")

    classe.nom_classe = classe_update.nom_classe
    classe.niveau = classe_update.niveau
    classe.filiere = classe_update.filiere
    classe.annee_scolaire = classe_update.annee_scolaire
    classe.effectif = classe_update.effectif

    if classe_update.id_enseignant:
        enseignants = db.query(Enseignant).filter(Enseignant.id_enseignant.in_(classe_update.id_enseignant)).all()
        if not enseignants:
            raise HTTPException(status_code=404, detail="Enseignant introuvable")
        classe.enseignants = enseignants
    else:
        classe.enseignants = []

    db.commit()
    db.refresh(classe)
    return classe

#Assigner un enseignant à une classe
@router.post("/assigner_enseignant/{classe_id}/{enseignant_id}", response_model=ClasseResponse)
async def assign_teacher_to_class(
    classe_id: int,
    enseignant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Action réservée à l’administrateur")

    classe = db.query(Classe).filter(Classe.id_classe == classe_id).first()
    if not classe:
        raise HTTPException(status_code=404, detail="Classe introuvable")

    enseignant = db.query(Enseignant).filter(Enseignant.id_enseignant == enseignant_id).first()
    if not enseignant:
        raise HTTPException(status_code=404, detail="Enseignant introuvable")

    if enseignant in classe.enseignants:
        raise HTTPException(status_code=400, detail="L'enseignant est déjà assigné à cette classe")

    classe.enseignants.append(enseignant)
    db.commit()
    db.refresh(classe)
    return classe

#Retirer un enseignant d'une classe
@router.delete("/retirer_enseignant/{classe_id}/{enseignant_id}", response_model=ClasseResponse)
async def remove_teacher_from_class(
    classe_id: int,
    enseignant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Action réservée à l’administrateur")

    classe = db.query(Classe).filter(Classe.id_classe == classe_id).first()
    if not classe:
        raise HTTPException(status_code=404, detail="Classe introuvable")

    enseignant = db.query(Enseignant).filter(Enseignant.id_enseignant == enseignant_id).first()
    if not enseignant:
        raise HTTPException(status_code=404, detail="Enseignant introuvable")

    if enseignant not in classe.enseignants:
        raise HTTPException(status_code=400, detail="L'enseignant n'est pas assigné à cette classe")

    classe.enseignants.remove(enseignant)
    db.commit()
    db.refresh(classe)
    return classe

#Ajouter un étudiant à une classe
@router.post("/ajouter_etudiant/{classe_id}/{etudiant_id}", response_model=ClasseResponse)
async def add_student_to_class(
    classe_id: int,
    etudiant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Action réservée à l’administrateur")

    classe = db.query(Classe).filter(Classe.id_classe == classe_id).first()
    if not classe:
        raise HTTPException(status_code=404, detail="Classe introuvable")

    etudiant = db.query(Etudiant).filter(Etudiant.id_etudiant == etudiant_id).first()
    if not etudiant:
        raise HTTPException(status_code=404, detail="Étudiant introuvable")

    if etudiant.id_classe == classe.id_classe:
        raise HTTPException(status_code=400, detail="L'étudiant est déjà dans cette classe")

    classe.effectif += 1
    etudiant.classe = classe

    db.commit()
    db.refresh(classe)
    return classe

#Retirer un étudiant d'une classe
@router.delete("/retirer_etudiant/{classe_id}/{etudiant_id}", response_model=ClasseResponse)
async def remove_student_from_class(
    classe_id: int,
    etudiant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Action réservée à l’administrateur")

    classe = db.query(Classe).filter(Classe.id_classe == classe_id).first()
    if not classe:
        raise HTTPException(status_code=404, detail="Classe introuvable")

    etudiant = db.query(Etudiant).filter(Etudiant.id_etudiant == etudiant_id).first()
    if not etudiant:
        raise HTTPException(status_code=404, detail="Étudiant introuvable")

    if etudiant.id_classe != classe.id_classe:
        raise HTTPException(status_code=400, detail="L'étudiant n'est pas dans cette classe")
    
    etudiant.classe = None

    if classe.effectif: 
        classe.effectif -= 1
    

    db.commit()
    db.refresh(classe)
    return classe

# Lister les étudiants d'une classe
@router.get("/etudiants_classe/{classe_id}", response_model=list[EtudiantDetail])
async def list_students_in_class(
    classe_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role.value != "admin" and current_user.role.value != "enseignant":
        raise HTTPException(status_code=403, detail="Accès réservé à l’administrateur")

    classe = db.query(Classe).filter(Classe.id_classe == classe_id).first()
    if not classe:
        raise HTTPException(status_code=404, detail="Classe introuvable")

    etudiants = db.query(Etudiant).filter(Etudiant.id_classe == classe_id).all()
    return [etudiant for etudiant in etudiants]

# Lister les enseignants d'une classe
@router.get("/enseignants_classe/{classe_id}", response_model=list[UserResponse])
async def list_teachers_in_class(
    classe_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role.value != "admin" and current_user.role.value != "enseignant" and current_user.role != "etudiant":
        raise HTTPException(status_code=403, detail="Accès réservé à l’administrateur")

    classe = db.query(Classe).filter(Classe.id_classe == classe_id).first()
    if not classe:
        raise HTTPException(status_code=404, detail="Classe introuvable")

    enseignants = classe.enseignants
    return [enseignant for enseignant in enseignants]

