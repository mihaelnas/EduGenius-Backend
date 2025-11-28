from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from datetime import timedelta, datetime
from app.Model import utilisateur_model as models
from app.DB.database import get_db
from app.Sec.Auth import verify_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, get_current_user, REFRESH_TOKEN_EXPIRE_DAYS
from passlib.context import CryptContext
from app.utils.email_sender import send_reset_email
from app.Model.utilisateur_model import User
from app.Model.resetToken_model import ResetToken
from app.Model.enseignant_model import Enseignant
import secrets

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/Connexion")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def login_response(user: models.User, db: Session):
    # Création de l'access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "role": user.role.value},
        expires_delta=access_token_expires
    )

    # Création du refresh token
    refresh_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token = create_access_token(
        data={"sub": user.email, "role": user.role.value},
        expires_delta=refresh_token_expires
    )

    # -----------------------------
    #  Récupération des infos selon le rôle
    # -----------------------------

    if user.role.value == "admin":
        user_info = {
            "nom": user.nom,
            "prenom": user.prenom,
            "nom_utilisateur": user.nom_utilisateur,
            "email": user.email
        }

    elif user.role.value == "enseignant":
        enseignant = db.query(Enseignant).filter(Enseignant.id_enseignant == user.id).first()
        if not enseignant:
            raise HTTPException(status_code=404, detail="Enseignant non trouvé")

        user_info = {
            "nom": user.nom,
            "prenom": user.prenom,
            "nom_utilisateur": user.nom_utilisateur,
            "email": user.email,
            "specialite": enseignant.specialite,
            "email_pro": enseignant.email_pro,
            "genre": enseignant.genre,
            "telephone": enseignant.telephone,
            "adresse": enseignant.adresse,
            "photo_url": enseignant.photo_url
        }

    elif user.role.value == "etudiant":
        etudiant = db.query(models.Etudiant).filter(models.Etudiant.id_etudiant == user.id).first()
        if not etudiant:
            raise HTTPException(status_code=404, detail="Étudiant non trouvé")

        user_info = {
            "nom": user.nom,
            "prenom": user.prenom,
            "nom_utilisateur": user.nom_utilisateur,
            "email": user.email,
            "matricule": etudiant.matricule,
            "date_naissance": etudiant.date_naissance,
            "genre": etudiant.genre,
            "telephone": etudiant.telephone,
            "adresse": etudiant.adresse,
            "photo_url": etudiant.photo_url
        }

    else:
        raise HTTPException(status_code=400, detail="Rôle utilisateur inconnu")

    # -----------------------------
    #  Création de la réponse API
    # -----------------------------
    response = JSONResponse(
        content={
            "message": "Connexion réussie",
            "role": user.role.value,
            "user_info": user_info,
            "redirect_to": f"/dashboard/{user.role.value}",
        }
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        samesite="lax",
        secure=False,
    )

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        samesite="lax",
        secure=False,
    )

    return response


# -------------------------------------------------------
#  ROUTE : Connexion
# -------------------------------------------------------
@router.post("/Connexion")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()

    if not user or not verify_password(form_data.password, user.mot_de_passe):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect",
        )
    print("Utilisateur connecté :", user.role.value) 
    return login_response(user, db)


# -------------------------------------------------------
#  Demande de reset password
# -------------------------------------------------------
@router.post("/reset-password-request")
def reset_password_request(email: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(status_code=404, detail="Email introuvable")

    token = secrets.token_urlsafe(32)

    reset_token = ResetToken(
        token=token,
        user_id=user.id,
        expires_at=datetime.utcnow() + timedelta(hours=1)
    )

    db.add(reset_token)
    db.commit()

    reset_link = f"https://votresite.com/reset-password?token={token}"

    send_reset_email(user.email, reset_link)

    return {"message": "Un email de réinitialisation a été envoyé."}


# -------------------------------------------------------
#  Réinitialisation du mot de passe
# -------------------------------------------------------
@router.post("/reset-password")
def reset_password(token: str, new_password: str, db: Session = Depends(get_db)):
    reset_token = db.query(ResetToken).filter(ResetToken.token == token).first()

    if not reset_token:
        raise HTTPException(status_code=400, detail="Token invalide")

    if reset_token.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Token expiré")

    user = reset_token.user

    user.mot_de_passe = pwd_context.hash(new_password)

    db.delete(reset_token)
    db.commit()

    return {"message": "Mot de passe réinitialisé avec succès !"}


# me 
@router.get("/me")
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    # Retourne user info + role
    return {
        "role": current_user.role.value,
        "user_info": {
            "nom": current_user.nom,
            "prenom": current_user.prenom,
            "nom_utilisateur": current_user.nom_utilisateur,
            "email": current_user.email
        }
    }