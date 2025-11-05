from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from DB.database import get_db
from Model.cours_model import Cours
from Schema.cours_schema import CoursCreate, CoursResponse
from Sec.Auth import get_current_user
from Model.utilisateur_model import User

router = APIRouter()


# 🧱 Créer un cours
@router.post("/ajouter", response_model=CoursResponse, status_code=status.HTTP_201_CREATED)
def create_cours(cours: CoursCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Seuls les profs et admins peuvent créer des cours
    if current_user.role.value != "enseignant":
        raise HTTPException(status_code=403, detail="Accès refusé")

    new_cours = Cours(
        titre=cours.titre,
        contenu=cours.contenu,
        type_cours=cours.type_cours,
        duree_estimee=cours.duree_estimee,
        id_enseignant=current_user.id,
        id_matiere=cours.id_matiere,
        id_classe=cours.id_classe
    )

    db.add(new_cours)
    db.commit()
    db.refresh(new_cours)
    return new_cours


# 📜 Lister tous les cours
@router.get("/enseignant/{id_enseignant}", response_model=list[CoursResponse])
def list_cours(id_enseignant: int ,db: Session = Depends(get_db)):
    cours = db.query(Cours).filter(Cours.id_enseignant == id_enseignant).all()
    if not cours :
        raise HTTPException(status_code=404, detail="Aucun cours")
    return cours


# 🔍 Récupérer un cours par ID
@router.get("/{cours_id}", response_model=CoursResponse)
def get_cours(cours_id: int, db: Session = Depends(get_db)):
    cours = db.query(Cours).filter(Cours.id_cours == cours_id).first()
    if not cours:
        raise HTTPException(status_code=404, detail="Cours non trouvé")
    return cours


# ✏️ Modifier un cours
@router.put("/{cours_id}", response_model=CoursResponse)
def update_cours(cours_id: int, updated_cours: CoursCreate, db: Session = Depends(get_db), current_user: User=Depends(get_current_user)):
    cours = db.query(Cours).filter(Cours.id_cours == cours_id).first()
    if not cours:
        raise HTTPException(status_code=404, detail="Cours non trouvé")

    # Seul le prof du cours ou l’admin peut le modifier
    if current_user.id != cours.id_enseignant:
        raise HTTPException(status_code=403, detail="Accès refusé")

    cours.titre = updated_cours.titre
    cours.contenu = updated_cours.contenu
    cours.type_cours = updated_cours.type_cours
    cours.duree_estimee = updated_cours.duree_estimee
    cours.id_enseignant = updated_cours.id_enseignant
    cours.id_matiere = updated_cours.id_matiere
    cours.id_classe = updated_cours.id_classe
    db.commit()
    db.refresh(cours)
    return cours


# 🗑️ Supprimer un cours
@router.delete("/{cours_id}", status_code=status.HTTP_200_OK)
def delete_cours(cours_id: int, db: Session = Depends(get_db), current_user: User =Depends(get_current_user)):
    cours = db.query(Cours).filter(Cours.id_cours == cours_id).first()
    if not cours:
        raise HTTPException(status_code=404, detail="Cours non trouvé")

    # Seul le prof du cours ou l’admin peut le supprimer
    if current_user.role.value != "admin" and current_user.id != cours.id_enseignant:
        raise HTTPException(status_code=403, detail="Accès refusé")

    db.delete(cours)
    db.commit()
    return {"message": "Cours supprimé avec succès"}
