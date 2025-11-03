from fastapi import APIRouter, Depends, HTTPException
from Sec.Auth import get_current_user

router = APIRouter()

@router.get("/")
def student_dashboard(current_user  = Depends(get_current_user)):
    if current_user.role.value != "etudiant":
        raise HTTPException(status_code=403, detail="Access forbidden")
    return {"message": f"Bienvenue {current_user.nom} !"}
