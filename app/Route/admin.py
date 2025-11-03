from fastapi import APIRouter, Depends, HTTPException, status
from Sec.Auth import get_current_user
from DB.database import get_db
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from Model.utilisateur_model import User, UserRole
from Schema.utilisateurs_schema import UserCreate, UserResponse, UserUpdate

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter()

""" CRUD pour les professeurs (seulement par un admin) """

# ✅ Tableau de bord admin
@router.get("/")
def admin_dashboard(current_user: User = Depends(get_current_user)):
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Access forbidden")
    return {"message": f"Bienvenue admin {current_user.nom}, vous etes connectee !"}


# ✅ Ajouter un professeur (seulement par un admin)
@router.post("/ajouter_professeur", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def add_professor(user: UserCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Access forbidden")

    db_user = db.query(User).filter((User.email == user.email) | (User.nom_utilisateur == user.nom_utilisateur)).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email ou nom d'utilisateur déjà utilisé")
    
    hashed_password = pwd_context.hash(user.mot_de_passe)
    new_user = User(
        nom=user.nom,
        prenom=user.prenom,
        nom_utilisateur=user.nom_utilisateur,
        email=user.email,
        mot_de_passe=hashed_password,
        role=UserRole.enseignant
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# ✅ Lister tous les professeurs
@router.get("/professeurs", response_model=list[UserResponse])
async def list_professors(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Accès réservé à l’administrateur")

    profs = db.query(User).filter(User.role == UserRole.enseignant).all()
    return profs

# ✅ Modifier un professeur
@router.put("/modifier_professeur/{prof_id}", response_model=UserResponse)
async def update_professor(
    prof_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Action réservée à l’administrateur")

    prof = db.query(User).filter(User.id == prof_id, User.role == UserRole.enseignant).first()
    if not prof:
        raise HTTPException(status_code=404, detail="Professeur introuvable")

    # Mise à jour des champs
    prof.nom = user_update.nom
    prof.prenom = user_update.prenom
    prof.nom_utilisateur = user_update.nom_utilisateur
    prof.email = user_update.email
    prof.mot_de_passe = pwd_context.hash(user_update.mot_de_passe)

    db.commit()
    db.refresh(prof)
    return prof


# ✅ Supprimer un professeur
@router.delete("/supprimer_professeur/{prof_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_professor(
    prof_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Action réservée à l’administrateur")

    prof = db.query(User).filter(User.id == prof_id, User.role == UserRole.enseignant).first()
    if not prof:
        raise HTTPException(status_code=404, detail="Professeur introuvable")

    db.delete(prof)
    db.commit()
    return {"message": f"Le professeur {prof.nom} {prof.prenom} a été supprimé avec succès."}


""" CRUD pour les étudiants (seulement par un admin) """
# ✅ Ajouter un étudiant
@router.post("/ajouter_etudiant", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def add_student(
    user: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Action réservée à l’administrateur")

    db_user = db.query(User).filter(
        (User.email == user.email) | (User.nom_utilisateur == user.nom_utilisateur)
    ).first()

    if db_user:
        raise HTTPException(status_code=400, detail="Email ou nom d'utilisateur déjà utilisé")

    hashed_password = pwd_context.hash(user.mot_de_passe)

    new_student = User(
        nom=user.nom,
        prenom=user.prenom,
        nom_utilisateur=user.nom_utilisateur,
        email=user.email,
        mot_de_passe=hashed_password,
        role=UserRole.etudiant
    )

    db.add(new_student)
    db.commit()
    db.refresh(new_student)
    return new_student


# ✅ Modifier un étudiant
@router.put("/modifier_etudiant/{etudiant_id}", response_model=UserResponse)
async def update_student(
    etudiant_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Action réservée à l’administrateur")

    etudiant = db.query(User).filter(User.id == etudiant_id, User.role == UserRole.etudiant).first()
    if not etudiant:
        raise HTTPException(status_code=404, detail="Étudiant introuvable")

    if user_update.nom:
        etudiant.nom = user_update.nom
    if user_update.prenom:
        etudiant.prenom = user_update.prenom
    if user_update.nom_utilisateur:
        etudiant.nom_utilisateur = user_update.nom_utilisateur
    if user_update.email:
        etudiant.email = user_update.email
    if user_update.mot_de_passe:
        etudiant.mot_de_passe = pwd_context.hash(user_update.mot_de_passe)

    db.commit()
    db.refresh(etudiant)
    return etudiant


# ✅ Supprimer un étudiant
@router.delete("/supprimer_etudiant/{etudiant_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_student(
    etudiant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Action réservée à l’administrateur")

    etudiant = db.query(User).filter(User.id == etudiant_id, User.role == UserRole.etudiant).first()
    if not etudiant:
        raise HTTPException(status_code=404, detail="Étudiant introuvable")

    db.delete(etudiant)
    db.commit()
    return {"message": f"L'étudiant {etudiant.nom} {etudiant.prenom} a été supprimé avec succès."}


# ✅ Lister tous les étudiants
@router.get("/etudiants", response_model=list[UserResponse])
async def list_students(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Accès réservé à l’administrateur")

    etudiants = db.query(User).filter(User.role == UserRole.etudiant).all()
    return etudiants