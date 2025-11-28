from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.DB.database import get_db
from app.Model.cours_model import Cours
from app.Model.matiere_model import Matiere
from app.Model.enseignant_model import Enseignant
from app.Model.etudiant_model import Etudiant
from app.Schema.cours_schema import CoursCreate, CoursResponse
from app.Sec.Auth import get_current_user
from app.Model.utilisateur_model import User

router = APIRouter()


# 🧱 Créer un cours
@router.post("/ajouter", response_model=CoursResponse, status_code=status.HTTP_201_CREATED)
def create_cours(
    cours: CoursCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    # Seuls les enseignants peuvent créer des cours
    if current_user.role.value != "enseignant":
        raise HTTPException(status_code=403, detail="Accès refusé")

    # Vérifier que l’enseignant est associé à la matière
    matiere = (
        db.query(Matiere)
        .join(Matiere.enseignants)
        .filter(
            Matiere.id_matiere == cours.id_matiere,
            Enseignant.id_enseignant == current_user.id
        )
        .first()
    )

    if not matiere:
        raise HTTPException(
            status_code=403,
            detail="Vous n'êtes pas autorisé à créer un cours pour cette matière"
        )

    # Création du cours
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

# 🔍 Lister les cours d’un enseignant avec contrôle d’accès
@router.get("/{id_enseignant}", response_model=list[CoursResponse])
def list_cours(
    id_enseignant: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # ----- ADMIN -----
    if current_user.role.value == "admin":
        cours = db.query(Cours).filter(Cours.id_enseignant == id_enseignant).all()
        if not cours:
            raise HTTPException(status_code=404, detail="Aucun cours trouvé")
        return cours

    # ----- ENSEIGNANT -----
    if current_user.role.value == "enseignant":
        # Un prof ne peut voir que ses propres cours
        if current_user.id != id_enseignant:
            raise HTTPException(status_code=403, detail="Accès refusé")

        cours = db.query(Cours).filter(Cours.id_enseignant == id_enseignant).all()
        if not cours:
            raise HTTPException(status_code=404, detail="Aucun cours trouvé")
        return cours

    # ----- ETUDIANT -----
    if current_user.role.value == "etudiant":
        # Liste des classes de l’étudiant
        etudiant = db.query(Etudiant).filter(Etudiant.id_etudiant == current_user.id).first()
        if not etudiant:
            raise HTTPException(status_code=404, detail="Étudiant introuvable")

        classes_etudiant = {c.id_classe for c in etudiant.classes}

        # Cours donnés par cet enseignant dans les classes de l’étudiant
        cours = (
            db.query(Cours)
            .filter(
                Cours.id_enseignant == id_enseignant,
                Cours.id_classe.in_(classes_etudiant)
            )
            .all()
        )

        if not cours:
            raise HTTPException(status_code=403, detail="Aucun accès aux cours de cet enseignant")

        return cours

    # Aucun autre rôle
    raise HTTPException(status_code=403, detail="Accès interdit")


# # 🔍 Récupérer un cours par ID avec contrôle d’accès
@router.get("/{cours_id}", response_model=CoursResponse)
def get_cours(
    cours_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    role = current_user.role.value

    # --- Vérification des rôles autorisés ---
    if role not in ["admin", "enseignant", "etudiant"]:
        raise HTTPException(status_code=403, detail="Accès refusé")

    cours = db.query(Cours).filter(Cours.id_cours == cours_id).first()
    if not cours:
        raise HTTPException(status_code=404, detail="Cours non trouvé")

    # --- ADMIN : peut tout voir ---
    if role == "admin":
        return cours

    # --- ENSEIGNANT : ne peut voir que ses cours ---
    if role == "enseignant":
        if cours.id_enseignant != current_user.id:
            raise HTTPException(status_code=403, detail="Vous n'avez pas accès à ce cours")
        return cours

    # --- ETUDIANT : doit appartenir à la classe du cours ---
    if role == "etudiant":
        etudiant = db.query(Etudiant).filter(Etudiant.id_etudiant == current_user.id).first()
        if not etudiant:
            raise HTTPException(status_code=404, detail="Étudiant introuvable")

        classes_etudiant = {c.id_classe for c in etudiant.classes}

        if cours.id_classe not in classes_etudiant:
            raise HTTPException(status_code=403, detail="Vous n'avez pas accès à ce cours")

        return cours

    # fallback
    raise HTTPException(status_code=403, detail="Accès refusé")



# ✏️ Modifier un cours
@router.put("/{cours_id}", response_model=CoursResponse)
def update_cours(cours_id: int, updated_cours: CoursCreate, db: Session = Depends(get_db), current_user: User=Depends(get_current_user)):
    cours = db.query(Cours).filter(Cours.id_cours == cours_id).first()
    if not cours:
        raise HTTPException(status_code=404, detail="Cours non trouvé")

    # Seul le prof du cours peut le modifier
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


# 🔍 Récupérer tous les cours d’un enseignant pour ses matières
@router.get("/{id_enseignant}/matieres", response_model=list[CoursResponse])
def get_cours_by_enseignant_matieres(
    id_enseignant: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Vérification d’accès
    if current_user.role.value not in ["enseignant", "admin"]:
        raise HTTPException(status_code=403, detail="Accès refusé")

    # Requête : récupérer tous les cours dont la matière appartient à l’enseignant
    cours = (
        db.query(Cours)
        .join(Cours.matieres)
        .join(Matiere.enseignants) 
        .filter(Enseignant.id_enseignant == id_enseignant)
        .all()
    )

    if not cours:
        raise HTTPException(status_code=404, detail="Aucun cours trouvé pour cet enseignant")

    return cours

# 🔍 Récupérer tous les cours d’un étudiant pour ses matières
@router.get("/{id_etudiant}/matieres", response_model=list[CoursResponse])
def get_cours_by_etudiant_matieres(
    id_etudiant: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Vérification d’accès
    if current_user.role.value not in ["etudiant", "admin"]:
        raise HTTPException(status_code=403, detail="Accès refusé")

    # Récupérer l’étudiant et ses classes
    etudiant = db.query(Etudiant).filter(Etudiant.id_etudiant == id_etudiant).first()
    if not etudiant:
        raise HTTPException(status_code=404, detail="Étudiant introuvable")

    classes_etudiant = {c.id_classe for c in etudiant.classes}

    # Requête : récupérer tous les cours dont la matière appartient aux professeurs des classes de l’étudiant
    cours = (
        db.query(Cours)
        .join(Cours.matieres)
        .join(Matiere.enseignants)
        .join(Enseignant.classes)
        .filter(Cours.id_classe.in_(classes_etudiant))
        .all()
    )

    if not cours:
        raise HTTPException(status_code=404, detail="Aucun cours trouvé pour cet étudiant")

    return cours

