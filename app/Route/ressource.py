from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from typing import List
from app.DB.database import get_db
from app.Sec.Auth import get_current_user
from app.Model.utilisateur_model import User
from app.Model.ressource_model import Ressource
from app.Model.cours_model import Cours
from app.Schema.ressource_schema import RessourceCreate, RessourceResponse

router = APIRouter(prefix="/cours", tags=["Ressources"])

# POST /cours/{id_cours}/ressources
@router.post("/{id_cours}/ressources", response_model=List[RessourceResponse], status_code=status.HTTP_201_CREATED)
def add_resources_to_course(
    id_cours: int,
    payload: List[RessourceCreate],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    cours = db.query(Cours).filter(Cours.id_cours == id_cours).first()
    if not cours:
        raise HTTPException(status_code=404, detail="Cours introuvable")

    # Vérifier que l'enseignant est bien le créateur du cours (ou admin)
    if current_user.role.value != "admin" and cours.id_enseignant != current_user.id:
        raise HTTPException(status_code=403, detail="Accès refusé")

    ressources = []
    for r in payload:
        res = Ressource(
            titre=r.titre,
            type_resource=r.type_resource,
            url=str(r.url),
            id_cours=id_cours,
            id_enseignant=current_user.id
        )
        db.add(res)
        ressources.append(res)

    db.commit()
    # refresh to get ids / timestamps
    for res in ressources:
        db.refresh(res)

    return ressources

# GET /cours/{id_cours}/ressources
@router.get("/{id_cours}/ressources", response_model=List[RessourceResponse])
def list_resources_for_course(
    id_cours: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    cours = db.query(Cours).filter(Cours.id_cours == id_cours).first()
    if not cours:
        raise HTTPException(status_code=404, detail="Cours introuvable")

    # accès : admin / enseignant du cours / étudiants de la classe (si tu veux restreindre)
    if current_user.role.value != "admin" and current_user.role.value != "enseignant" and current_user.role.value != "etudiant":
        raise HTTPException(status_code=403, detail="Accès refusé")

    # optionally: if student, verify they belong to classe of the course

    ressources = db.query(Ressource).filter(Ressource.id_cours == id_cours).order_by(Ressource.created_at.desc()).all()
    return ressources

# PUT /ressources/{id_ressource}
@router.put("/ressources/{id_ressource}", response_model=RessourceResponse)
def update_resource(
    id_ressource: int,
    payload: RessourceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    res = db.query(Ressource).filter(Ressource.id_ressource == id_ressource).first()
    if not res:
        raise HTTPException(status_code=404, detail="Ressource introuvable")

    if current_user.role.value != "admin" and res.id_enseignant != current_user.id:
        raise HTTPException(status_code=403, detail="Accès refusé")

    res.titre = payload.titre
    res.type_resource = payload.type_resource
    res.url = str(payload.url)

    db.commit()
    db.refresh(res)
    return res

# DELETE /ressources/{id_ressource}
@router.delete("/ressources/{id_ressource}", status_code=status.HTTP_204_NO_CONTENT)
def delete_resource(
    id_ressource: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    res = db.query(Ressource).filter(Ressource.id_ressource == id_ressource).first()
    if not res:
        raise HTTPException(status_code=404, detail="Ressource introuvable")

    if current_user.role.value != "admin" and res.id_enseignant != current_user.id:
        raise HTTPException(status_code=403, detail="Accès refusé")

    db.delete(res)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
