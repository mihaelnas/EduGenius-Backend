from fastapi import APIRouter , Depends , status , HTTPException
from sqlalchemy.orm import Session
from app.DB.database import get_db
from app.Model.matiere_model import Matiere
from app.Model.utilisateur_model import User
from app.Model.enseignant_model import Enseignant
from app.Schema.matiere_schema import MatiereCreate , MatiereResponse
from app.Sec.Auth import get_current_user

router = APIRouter(prefix="/dashboard/admin/matieres", tags=["Matiere"])


#Creer une matiere
@router.post("/ajouter", response_model = MatiereResponse , status_code=status.HTTP_201_CREATED  )
async def cree_matiere(matiere: MatiereCreate , db: Session = Depends(get_db), current_user : User = Depends(get_current_user) ):
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Accès refusé")
    
    new_matiere = Matiere(
        nom_matiere = matiere.nom_matiere,
        credit = matiere.credit,
        semestre = matiere.semestre,
        photo_url = matiere.photo_url,
        id_enseignant = matiere.id_enseignant
    )

    db.add(new_matiere)
    db.commit()
    db.refresh(new_matiere)
    return new_matiere


#Lister les matieres
@router.get("/", response_model=list[MatiereResponse])
def list_matiere(db: Session = Depends(get_db) , current_user: User = Depends(get_current_user)):
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Accès refusé")
    
    matiere = db.query(Matiere).all()
    if not matiere :
        raise HTTPException(status_code=404, detail="Aucun matiere")
    return matiere


# 🔍 Récupérer un matiere par ID
@router.get("/{id_matiere}", response_model=MatiereResponse)
def get_cours(id_matiere: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Accès refusé")
    
    matiere = db.query(Matiere).filter(Matiere.id_matiere == id_matiere).first()
    if not matiere:
        raise HTTPException(status_code=404, detail="Matiere non trouvé")
    return matiere


# ✏️ Modifier un matiere
@router.put("/{id_matiere}", response_model=MatiereResponse)
def update_matiere(id_matiere: int, updated_matiere: MatiereCreate, db: Session = Depends(get_db), current_user: User=Depends(get_current_user)):
    if current_user.role.value != "admin" | current_user.role.value != "enseignant":
        raise HTTPException(status_code=403, detail="Accès refusé")
    matiere = db.query(Matiere).filter(Matiere.id_matiere == id_matiere).first()
    
    if not matiere:
        raise HTTPException(status_code=404, detail="Matiere non trouvé")

    if updated_matiere.nom_matiere:
        matiere.nom_matiere = updated_matiere.nom_matiere
    if updated_matiere.credit :
        matiere.credit = updated_matiere.credit
    if updated_matiere.semestre:
        matiere.semestre = updated_matiere.semestre
    if updated_matiere.photo_url :
        matiere.photo_url = updated_matiere.photo_url

    db.commit()
    db.refresh(matiere)
    return matiere


#Supprimer une matiere
@router.delete("/{id_matiere}", status_code=status.HTTP_200_OK)
def delete_matiere(id_matiere: int, db: Session = Depends(get_db), current_user: User =Depends(get_current_user)):
    matiere = db.query(Matiere).filter(Matiere.id_matiere == id_matiere).first()
    if not matiere:
        raise HTTPException(status_code=404, detail="Matiere non trouvé")

    # Seul le prof du cours ou l’admin peut le supprimer
    if current_user.role.value != "admin" | (matiere.id_enseignant != current_user.id):
        raise HTTPException(status_code=403, detail="Accès refusé")

    db.delete(matiere)
    db.commit()
    return {"message": "Matiere supprimé avec succès"}

#Assigner un enseignant a un matiere
@router.post("/assigner_enseignant/{matiere_id}/{enseignant_id}", response_model=MatiereResponse)
async def assign_teacher_to_matiere(
    matiere_id: int,
    enseignant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Action réservée à l’administrateur")

    matiere = db.query(Matiere).filter(Matiere.id_matiere == matiere_id).first()
    if not matiere:
        raise HTTPException(status_code=404, detail="Matiere introuvable")

    enseignant = db.query(Enseignant).filter(Enseignant.id_enseignant == enseignant_id).first()
    if not enseignant:
        raise HTTPException(status_code=404, detail="Enseignant introuvable")

    if enseignant in matiere.enseignants:
        raise HTTPException(status_code=400, detail="L'enseignant est déjà assigné à cette matiere")

    matiere.id_enseignant = enseignant_id
    db.commit()
    db.refresh(matiere)
    return matiere

#Retirer un enseignant a une matiere
@router.delete("/retirer_enseignant/{matiere_id}/{enseignant_id}", response_model=MatiereResponse)
async def remove_teacher_from_matiere(
    matiere_id: int,
    enseignant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Action réservée à l’administrateur")

    matiere = db.query(Matiere).filter(Matiere.id_matiere == matiere_id).first()
    if not matiere:
        raise HTTPException(status_code=404, detail="Matiere introuvable")

    enseignant = db.query(Enseignant).filter(Enseignant.id_enseignant == enseignant_id).first()
    if not enseignant:
        raise HTTPException(status_code=404, detail="Enseignant introuvable")

    if enseignant not in matiere.enseignants:
        raise HTTPException(status_code=400, detail="L'enseignant n'est pas assigné à cette matiere")

    matiere.id_enseignant = None
    db.commit()
    db.refresh(matiere)
    return matiere

# Un enseignant peut voir ses matieres
@router.get("/enseignant/{enseignant_id}", response_model=list[MatiereResponse])
async def get_matieres_for_enseignant(
    enseignant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role.value != "admin" and current_user.role.value != "enseignant":
        raise HTTPException(status_code=403, detail="Accès réservé à l’administrateur ou à l’enseignant")

    if current_user.role.value == "enseignant" and current_user.id != enseignant_id:
        raise HTTPException(status_code=403, detail="Accès refusé aux autres enseignants")

    enseignant = db.query(Enseignant).filter(Enseignant.id_enseignant == enseignant_id).first()
    if not enseignant:
        raise HTTPException(status_code=404, detail="Enseignant introuvable")

    return enseignant.matieres