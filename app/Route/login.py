from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm , OAuth2PasswordBearer
from datetime import timedelta
from Model import utilisateur_model as models
from DB.database import SessionLocal
from Sec.Auth import verify_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES , get_current_user, REFRESH_TOKEN_EXPIRE_DAYS
from DB.database import get_db

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/Connexion")


def login_response(user: models.User):
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

    # Réponse avec les tokens dans les cookies HttpOnly
    response = JSONResponse(
        content={
            "message": "Connexion réussie",
            "role": user.role.value,
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

@router.post("/Connexion")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.mot_de_passe):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return login_response(user)