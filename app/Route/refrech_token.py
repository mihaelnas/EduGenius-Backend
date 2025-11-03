from fastapi import APIRouter, Request, Response, HTTPException, status
from Sec.Auth import create_access_token, SECRET_KEY, ALGORITHM
from jose import jwt, JWTError

router = APIRouter()

@router.post("/refresh_token")
def refresh_token(request: Request, response: Response):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token manquant")
    
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        role = payload.get("role")
        if email is None or role is None:
            raise HTTPException(status_code=401, detail="Refresh token invalide")
    except JWTError:
        raise HTTPException(status_code=401, detail="Refresh token invalide")
    
    # Générer un nouveau access token
    new_access_token = create_access_token({"sub": email, "role": role})
    response.set_cookie(
        key="access_token",
        value=new_access_token,
        httponly=True,
        samesite="lax",
        secure=False,
    )
    return {"message": "Token rafraîchi"}
