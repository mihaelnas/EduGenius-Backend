from fastapi import APIRouter, Depends, HTTPException, status, Response, Body 
from typing import Optional
from app.Sec.Auth import get_current_user
from app.DB.database import get_db
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from app.Model.utilisateur_model import User, UserRole, UserStatus
from app.Schema.utilisateurs_schema import UserCreate, UserResponse, UserUpdate
from app.Schema.etudiant_schema import EtudiantCreate, EtudiantUpdate , EtudiantDetail , AddStudentRequest , StudentUpdateRequest
from app.Schema.enseignant_schema import EnseignantCreate, EnseignantUpdate , EnseignantDetail , AddProfessorRequest , ProfessorUpdateRequest
from app.Model.etudiant_model import Etudiant
from app.Model.enseignant_model import Enseignant

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
async def add_professor(data:AddProfessorRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Access forbidden")

    user = data.user
    enseignant = data.enseignant

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

    new_enseignant = Enseignant(
        id_enseignant=new_user.id,
        specialite=enseignant.specialite,
        email_professionnel=enseignant.email_professionnel,
        genre=enseignant.genre,
        telephone=enseignant.telephone,
        adresse=enseignant.adresse,
        photo_url=enseignant.photo_url
    )
    db.add(new_enseignant)
    db.commit()
    db.refresh(new_enseignant)

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



@router.put("/modifier_professeur/{prof_id}", response_model=EnseignantDetail)
async def update_professor(
    prof_id: int,
    payload: ProfessorUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != UserRole.admin:
        raise HTTPException(403, "Action réservée à l’administrateur")

    prof = db.query(User).filter(
        User.id == prof_id,
        User.role == UserRole.enseignant
    ).first()

    if not prof:
        raise HTTPException(404, "Professeur introuvable")

    details = db.query(Enseignant).filter(
        Enseignant.id_enseignant == prof_id
    ).first()

    if not details:
        raise HTTPException(404, "Détails du professeur introuvables")

    user_update = payload.user
    ens_update = payload.enseignant

    # Normalisation téléphone
    def normalize_phone(phone: Optional[str]):
        import re
        if not phone:
            return None
        return re.sub(r"\D", "", phone)

    try:
        # ------------------ USER UPDATE ------------------
        if user_update:
            if user_update.nom is not None:
                prof.nom = user_update.nom
            if user_update.prenom is not None:
                prof.prenom = user_update.prenom
            if user_update.nom_utilisateur is not None:
                existe = db.query(User).filter(
                    User.nom_utilisateur == user_update.nom_utilisateur,
                    User.id != prof_id
                ).first()
                if existe:
                    raise HTTPException(409, "Nom d'utilisateur déjà utilisé")
                prof.nom_utilisateur = user_update.nom_utilisateur
            if user_update.email is not None:
                existe = db.query(User).filter(
                    User.email == user_update.email,
                    User.id != prof_id
                ).first()
                if existe:
                    raise HTTPException(409, "Email déjà utilisé")
                prof.email = user_update.email
            if user_update.mot_de_passe is not None:
                prof.mot_de_passe = pwd_context.hash(user_update.mot_de_passe)

        # ------------------ ENSEIGNANT UPDATE ------------------
        if ens_update:
            if ens_update.specialite is not None:
                details.specialite = ens_update.specialite
            if ens_update.email_professionnel is not None:
                existe = db.query(Enseignant).filter(
                    Enseignant.email_professionnel == ens_update.email_professionnel,
                    Enseignant.id_enseignant != prof_id
                ).first()
                if existe:
                    raise HTTPException(409, "Email professionnel déjà utilisé")
                details.email_professionnel = ens_update.email_professionnel
            if ens_update.genre is not None:
                details.genre = ens_update.genre
            if ens_update.telephone is not None:
                tel = normalize_phone(ens_update.telephone)
                if tel:
                    existe = db.query(Enseignant).filter(
                        Enseignant.telephone == tel,
                        Enseignant.id_enseignant != prof_id
                    ).first()
                    if existe:
                        raise HTTPException(409, "Numéro de téléphone déjà utilisé")
                    details.telephone = tel
            if ens_update.adresse is not None:
                details.adresse = ens_update.adresse
            if ens_update.photo_url is not None:
                details.photo_url = ens_update.photo_url
     
        # Commit toutes les modifications
        db.commit()
        db.refresh(prof)
        db.refresh(details)

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        import logging, traceback
        logging.error(traceback.format_exc())
        raise HTTPException(500, "Erreur lors de la mise à jour du professeur")

    return EnseignantDetail(
        user=UserResponse(**prof.__dict__),
        specialite=details.specialite,
        email_professionnel=details.email_professionnel,
        genre=details.genre,
        telephone=details.telephone,
        adresse=details.adresse,
        photo_url=details.photo_url,
    )

# ✅ Supprimer un professeur
@router.delete("/supprimer_professeur/{prof_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_professor(
    prof_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Action réservée à l’administrateur")
    
    enseignant = db.query(User).filter(User.id == prof_id).first()
    prof = db.query(Enseignant).filter(Enseignant.id_enseignant == prof_id).first()
    if prof:
        db.delete(prof)
        db.commit()
    else:
        raise HTTPException(status_code=404, detail="Professeur introuvable")

    db.delete(enseignant)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# Details d'un professeur
@router.get("/professeur/{prof_id}", response_model=EnseignantDetail)
async def get_professor_details(
    prof_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role.value != "admin" and current_user.role.value != "enseignant":
        raise HTTPException(status_code=403, detail="Accès réservé à l’administrateur")

    prof = db.query(Enseignant).filter(Enseignant.id_enseignant == prof_id).first()
    if not prof:
        raise HTTPException(status_code=404, detail="Professeur introuvable")

    return prof


""" CRUD pour les étudiants (seulement par un admin) """
# ✅ Ajouter un étudiant
@router.post("/ajouter_etudiant", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def add_student(
    data:AddStudentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user = data.user
    etudiant = data.etudiant


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
        status=UserStatus.inactif,
        role=UserRole.etudiant
        
    )

    db.add(new_student)
    db.commit()
    db.refresh(new_student)

    new_etudiant = Etudiant(
        id_etudiant=new_student.id,
        matricule=etudiant.matricule,
        date_naissance=etudiant.date_naissance,
        lieu_naissance=etudiant.lieu_naissance,
        genre=etudiant.genre,
        adresse=etudiant.adresse,
        niveau_etude=etudiant.niveau_etude,
        telephone=etudiant.telephone,
        filiere=etudiant.filiere,
        photo_url=etudiant.photo_url
    )
    db.add(new_etudiant)
    db.commit()
    db.refresh(new_etudiant)
    return new_student



@router.put("/modifier_etudiant/{etudiant_id}", response_model=EtudiantDetail)
async def update_student(
    etudiant_id: int,
    payload: StudentUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # --- Sécurité ---
    if current_user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="Action réservée à l’administrateur")

    # --- Récupération User ---
    etudiant = db.query(User).filter(
        User.id == etudiant_id,
        User.role == UserRole.etudiant
    ).first()

    if not etudiant:
        raise HTTPException(status_code=404, detail="Étudiant introuvable")

    # --- Récupération détails ---
    details = db.query(Etudiant).filter(
        Etudiant.id_etudiant == etudiant_id
    ).first()

    if not details:
        raise HTTPException(status_code=404, detail="Détails de l'étudiant introuvables")

    user_update = payload.user
    etu_update = payload.etudiant

    # --- Normalisation téléphone ---
    def normalize_phone(phone: str | None):
        import re
        if not phone:
            return None
        return re.sub(r"\D", "", phone)

    # ---------------- TRANSACTION ATOMIQUE ----------------
    try:
        # Pas besoin de `with db.begin()`, car Session est déjà transactionnelle par défaut
        # ---------- UPDATE USER ----------
        if user_update.nom is not None:
            etudiant.nom = user_update.nom

        if user_update.prenom is not None:
            etudiant.prenom = user_update.prenom

        if user_update.nom_utilisateur is not None:
            existe = db.query(User).filter(
                User.nom_utilisateur == user_update.nom_utilisateur,
                User.id != etudiant_id
            ).first()
            if existe:
                raise HTTPException(409, "Nom d'utilisateur déjà utilisé")
            etudiant.nom_utilisateur = user_update.nom_utilisateur

        if user_update.email is not None:
            existe = db.query(User).filter(
                User.email == user_update.email,
                User.id != etudiant_id
            ).first()
            if existe:
                raise HTTPException(409, "Email déjà utilisé")
            etudiant.email = user_update.email

        if user_update.mot_de_passe is not None:
            etudiant.mot_de_passe = pwd_context.hash(user_update.mot_de_passe)

        # ---------- UPDATE ÉTUDIANT ----------
        if etu_update.matricule is not None:
            existe = db.query(Etudiant).filter(
                Etudiant.matricule == etu_update.matricule,
                Etudiant.id_etudiant != etudiant_id
            ).first()
            if existe:
                raise HTTPException(409, "Matricule déjà utilisé")
            details.matricule = etu_update.matricule

        if etu_update.date_naissance is not None:
            details.date_naissance = etu_update.date_naissance

        if etu_update.genre is not None:
            details.genre = etu_update.genre

        if etu_update.lieu_naissance is not None:
            details.lieu_naissance = etu_update.lieu_naissance

        if etu_update.niveau_etude is not None:
            details.niveau_etude = etu_update.niveau_etude

        if etu_update.adresse is not None:
            details.adresse = etu_update.adresse

        if etu_update.telephone is not None:
            tel = normalize_phone(etu_update.telephone)
            if tel:
                existe = db.query(Etudiant).filter(
                    Etudiant.telephone == tel,
                    Etudiant.id_etudiant != etudiant_id
                ).first()
                if existe:
                    raise HTTPException(409, "Numéro de téléphone déjà utilisé")
                details.telephone = tel

        if etu_update.photo_url is not None:
            details.photo_url = etu_update.photo_url

        if etu_update.filiere is not None:
            details.filiere = etu_update.filiere

        # Commit explicit
        db.commit()
        db.refresh(etudiant)
        db.refresh(details)

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(500, detail=f"Erreur lors de la mise à jour de l'étudiant: {str(e)}")

    # --- Retour avec Pydantic v2 ---
    return EtudiantDetail(
        user=UserResponse(**etudiant.__dict__),  # ⚡ Pydantic v2
        matricule=details.matricule,
        date_naissance=details.date_naissance,
        genre=details.genre,
        lieu_naissance=details.lieu_naissance,
        niveau_etude=details.niveau_etude,
        adresse=details.adresse,
        telephone=details.telephone,
        photo_url=details.photo_url,
        filiere=details.filiere
    )


# ✅ Supprimer un étudiant
@router.delete("/supprimer_etudiant/{etudiant_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_student(
    etudiant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Action réservée à l’administrateur")

    etudiant = db.query(User).filter(User.id == etudiant_id, User.role == UserRole.etudiant.value).first()
    if not etudiant:
        raise HTTPException(status_code=404, detail="Étudiant introuvable")
    students = db.query(Etudiant).filter(Etudiant.id_etudiant == etudiant.id).first()
    if students:
        db.delete(students)
        db.commit()
    else:
        raise HTTPException(status_code=404, detail="Détails de l'étudiant introuvables")
    
    db.delete(etudiant)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)



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


# ✅ Obtenir les détails d'un étudiant
@router.get("/etudiant/{etudiant_id}", response_model=EtudiantDetail)
async def get_student_details(
    etudiant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role.value != "admin" and current_user.role.value != "enseignant":
        raise HTTPException(status_code=403, detail="Accès réservé à l’administrateur")

    etudiant = db.query(Etudiant).filter(Etudiant.id_etudiant == etudiant_id).first()
    if not etudiant:
        raise HTTPException(status_code=404, detail="Étudiant introuvable")

    return etudiant


""" CRUD pour creer une classe et lister les classes (seulement par un admin) """
