from fastapi import APIRouter, Depends , HTTPException , status
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from app.DB.database import SessionLocal
from app.Model.utilisateur_model import User, UserRole, UserStatus
from app.Model.etudiant_model import Etudiant  
from app.Schema.utilisateurs_schema import UserCreate, UserResponse
from app.Schema.etudiant_schema import EtudiantCreate, EtudiantResponse, EtudiantActivation

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/inscription", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def inscription_user(user: UserCreate, db: Session = Depends(get_db)):
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
        status=UserStatus.actif,
        role=UserRole.etudiant

    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


# Activation compte d'un etudiant via nom , prenom , matricule  et creation d'email et mot de passe
@router.post("/activation", response_model=EtudiantResponse, status_code=status.HTTP_200_OK)
async def activation_etudiant(activation_data: EtudiantActivation, db: Session = Depends(get_db)):
    etudiant = db.query(User).join(User.etudiants).filter(
        User.nom == activation_data.nom,
        User.prenom == activation_data.prenom,
        Etudiant.matricule == activation_data.matricule,
        User.role == UserRole.etudiant
    ).first()

    if not etudiant:
        raise HTTPException(status_code=404, detail="Étudiant introuvable")

    if etudiant.status == UserStatus.actif:
        raise HTTPException(status_code=400, detail="Compte déjà activé")

    # Mettre à jour l'email et le mot de passe
    etudiant.email = activation_data.email
    etudiant.mot_de_passe = pwd_context.hash(activation_data.mot_de_passe)
    etudiant.status = UserStatus.actif

    db.commit()
    db.refresh(etudiant)

    return etudiant.etudiants

