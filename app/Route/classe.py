from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from DB.database import get_db
from Model.classe_model import Classe
from Schema.classe_schema import ClasseCreate, ClasseResponse
from Sec.Auth import get_current_user
from Model.utilisateur_model import UserRole

router = APIRouter()

# 🧱 Ajouter une classe
@router.post("/ajouter", response_model=ClasseResponse, status_code=status.HTTP_201_CREATED)
def create_classe(classe: ClasseCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Accès refusé")
    
    new_classe = Classe(
        nom_classe=classe.nom_classe,
        niveau=classe.niveau,
        filiere=classe.filiere,
        annee_scolaire=classe.annee_scolaire,
        id_prof=classe.id_enseignant
    )
    db.add(new_classe)
    db.commit()
    db.refresh(new_classe)
    return new_classe


# 📜 Lister toutes les classes
@router.get("/", response_model=list[ClasseResponse])
def list_classes(db: Session = Depends(get_db)):
    return db.query(Classe).all()


# 🔍 Récupérer une classe par ID
@router.get("/{classe_id}", response_model=ClasseResponse)
def get_classe(classe_id: int, db: Session = Depends(get_db)):
    classe = db.query(Classe).filter(Classe.id_classe == classe_id).first()
    if not classe:
        raise HTTPException(status_code=404, detail="Classe non trouvée")
    return classe


# 🗑️ Supprimer une classe
@router.delete("/{classe_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_classe(classe_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Accès refusé")

    classe = db.query(Classe).filter(Classe.id_classe == classe_id).first()
    if not classe:
        raise HTTPException(status_code=404, detail="Classe non trouvée")
    db.delete(classe)
    db.commit()
    return {"message": "Classe supprimée avec succès"}

# ✏️ Mettre à jour une classe
@router.put("/{classe_id}", response_model=ClasseResponse)
def update_classe(classe_id: int, classe_update: ClasseCreate, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Accès refusé")

    classe = db.query(Classe).filter(Classe.id_classe == classe_id).first()
    if not classe:
        raise HTTPException(status_code=404, detail="Classe non trouvée")

    classe.nom_classe = classe_update.nom_classe
    classe.niveau = classe_update.niveau
    classe.filiere = classe_update.filiere
    classe.annee_scolaire = classe_update.annee_scolaire
    classe.id_enseignant = classe_update.id_enseignant

    db.commit()
    db.refresh(classe)
    return classe