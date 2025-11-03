from fastapi import APIRouter, Depends , HTTPException , status
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from DB.database import SessionLocal
from Model.utilisateur_model import User, UserRole
from Schema.utilisateurs_schema import UserCreate, UserResponse

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
        role=UserRole.etudiant
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
