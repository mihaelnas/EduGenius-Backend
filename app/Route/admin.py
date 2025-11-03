from fastapi import APIRouter, Depends, HTTPException, status, Response
from Sec.Auth import get_current_user
from DB.database import get_db
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from Model.utilisateur_model import User, UserRole
from Schema.utilisateurs_schema import UserCreate, UserResponse, UserUpdate
from Model.classe_model import Classe
from Schema.classe_schema import ClasseCreate, ClasseResponse
from Schema.etudiant_schema import EtudiantCreate, EtudiantUpdate , EtudiantDetail
from Schema.enseignant_schema import EnseignantCreate, EnseignantUpdate , EnseignantDetail
from Model.etudiant_model import Etudiant
from Model.enseignant_model import Enseignant

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
async def add_professor(enseignant:EnseignantCreate ,user: UserCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
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

# ✅ Modifier un professeur
@router.put("/modifier_professeur/{prof_id}", response_model=UserResponse)
async def update_professor(
    prof_id: int,
    user_update: UserUpdate,
    enseignant_update:EnseignantUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Action réservée à l’administrateur")

    prof = db.query(User).filter(User.id == prof_id, User.role == UserRole.enseignant).first()
    if not prof:
        raise HTTPException(status_code=404, detail="Professeur introuvable")

    # Mise à jour des champs
    if user_update.nom:
        prof.nom = user_update.nom
    if user_update.prenom:
        prof.prenom = user_update.prenom
    if user_update.nom_utilisateur:
        existe_user = db.query(User).filter(User.nom_utilisateur == user_update.nom_utilisateur, User.id != prof_id).first()
        if existe_user:
            raise HTTPException(status_code=400, detail="Nom d'utilisateur déjà utilisé")
        prof.nom_utilisateur = user_update.nom_utilisateur
    if user_update.email:
        existe_email = db.query(User).filter(User.email == user_update.email, User.id != prof_id).first()
        if existe_email:
            raise HTTPException(status_code=400, detail="Email déjà utilisé")
        prof.email = user_update.email
    if user_update.mot_de_passe:
        prof.mot_de_passe = pwd_context.hash(user_update.mot_de_passe)
    
    db.commit()
    db.refresh(prof)

    enseignant = db.query(Enseignant).filter(Enseignant.id_enseignant == prof.id).first()
    if not enseignant:
        raise HTTPException(status_code=404, detail="Détails du professeur introuvables")
    if enseignant_update.specialite:
        enseignant.specialite = enseignant_update.specialite
    if enseignant_update.email_professionnel:
        existe_email = db.query(Enseignant).filter(Enseignant.email_professionnel == enseignant_update.email_professionnel, Enseignant.id_enseignant != prof.id).first()
        if existe_email:
            raise HTTPException(status_code=400, detail="Email professionnel déjà utilisé")
        enseignant.email_professionnel = enseignant_update.email_professionnel
    if enseignant_update.genre:
        enseignant.genre = enseignant_update.genre
    if enseignant_update.telephone:
        existe_num = db.query(Enseignant).filter(Enseignant.telephone == enseignant_update.telephone, Enseignant.id_enseignant != prof.id).first()
        if existe_num:
            raise HTTPException(status_code=400, detail="Numéro de téléphone déjà utilisé")
        enseignant.telephone = enseignant_update.telephone
    if enseignant_update.adresse:
        enseignant.adresse = enseignant_update.adresse
    if enseignant_update.photo_url:
        enseignant.photo_url = enseignant_update.photo_url 

    db.commit()
    db.refresh(enseignant)


    return prof


# ✅ Supprimer un professeur
@router.delete("/supprimer_professeur/{prof_id}", status_code=status.HTTP_200_OK)
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
    return status.HTTP_200_OK


# Details d'un professeur
@router.get("/professeur/{prof_id}", response_model=EnseignantDetail)
async def get_professor_details(
    prof_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Accès réservé à l’administrateur")

    prof = db.query(Enseignant).filter(Enseignant.id_enseignant == prof_id).first()
    if not prof:
        raise HTTPException(status_code=404, detail="Professeur introuvable")

    return prof


""" CRUD pour les étudiants (seulement par un admin) """
# ✅ Ajouter un étudiant
@router.post("/ajouter_etudiant", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def add_student(
    user: UserCreate,
    etudiant: EtudiantCreate,
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


# ✅ Modifier un étudiant
@router.put("/modifier_etudiant/{etudiant_id}", response_model=UserResponse)
async def update_student(
    etudiant_id: int,
    user_update: UserUpdate,
    etudiant_update: EtudiantUpdate,
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
        existe_user = db.query(User).filter(User.nom_utilisateur == user_update.nom_utilisateur, User.id != etudiant_id).first()
        if existe_user:
            raise HTTPException(status_code=400, detail="Nom d'utilisateur déjà utilisé")
        etudiant.nom_utilisateur = user_update.nom_utilisateur
    if user_update.email:
        existe_email = db.query(User).filter(User.email == user_update.email, User.id != etudiant_id).first()
        if existe_email:
            raise HTTPException(status_code=400, detail="Email déjà utilisé")
        etudiant.email = user_update.email
    if user_update.mot_de_passe:
        etudiant.mot_de_passe = pwd_context.hash(user_update.mot_de_passe)

    db.commit()
    db.refresh(etudiant)
    
    students = db.query(Etudiant).filter(Etudiant.id_etudiant == etudiant.id).first()
    if not students:
        raise HTTPException(status_code=404, detail="Détails de l'étudiant introuvables")
    

    if etudiant_update.matricule:
        exist_matricule = db.query(Etudiant).filter(Etudiant.matricule == etudiant_update.matricule, Etudiant.id_etudiant != etudiant.id).first()
        if exist_matricule:
            raise HTTPException(status_code=400, detail="Matricule déjà utilisé")
        students.matricule = etudiant_update.matricule
    if etudiant_update.date_naissance:
        students.date_naissance = etudiant_update.date_naissance
    if etudiant_update.genre:
        students.genre = etudiant_update.genre
    if etudiant_update.adresse:
        students.adresse = etudiant_update.adresse
    if etudiant_update.telephone:
        exist_matricule = db.query(Etudiant).filter(Etudiant.telephone == etudiant_update.telephone, Etudiant.id_etudiant != etudiant.id).first()
        if exist_matricule:
            raise HTTPException(status_code=400, detail="Numéro de téléphone déjà utilisé")
        students.telephone = etudiant_update.telephone
    if etudiant_update.photo_url:
        students.photo_url = etudiant_update.photo_url
    if etudiant_update.filiere:
        students.filiere = etudiant_update.filiere

    db.commit()
    db.refresh(students)

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
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Accès réservé à l’administrateur")

    etudiant = db.query(Etudiant).filter(Etudiant.id_etudiant == etudiant_id).first()
    if not etudiant:
        raise HTTPException(status_code=404, detail="Étudiant introuvable")

    return etudiant


""" CRUD pour creer une classe et lister les classes (seulement par un admin) """

# ✅ Créer une classe
@router.post("/creer_classe", response_model=ClasseResponse, status_code=status.HTTP_201_CREATED)
async def create_class(
    classe: ClasseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Action réservée à l’administrateur")

    db_classe = db.query(Classe).filter(Classe.nom_classe == classe.nom_classe).first()
    if db_classe:
        raise HTTPException(status_code=400, detail="Une classe avec ce nom existe déjà")

    new_classe = Classe(
        nom_classe=classe.nom_classe,
        niveau=classe.niveau,
        filiere=classe.filiere,
        annee_scolaire=classe.annee_scolaire,
        effectif=classe.effectif or 0
    )

    if classe.id_enseignant:
        enseignants = db.query(Enseignant).filter(Enseignant.id_enseignant.in_(classe.id_enseignant)).all()
        if not enseignants:
            raise HTTPException(status_code=404, detail="Enseignant introuvable")
        new_classe.enseignants = enseignants 
    else:
        new_classe.enseignants = []

    db.add(new_classe)
    db.commit()
    db.refresh(new_classe)
    return new_classe

# ✅ Lister toutes les classes
@router.get("/classes", response_model=list[ClasseResponse])
async def list_classes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Accès réservé à l’administrateur")

    classes = db.query(Classe).all()
    return classes

# ✅ Obtenir les détails d'une classe
@router.get("/classe/{classe_id}", response_model=ClasseResponse)
async def get_class_details(
    classe_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Accès réservé à l’administrateur")

    classe = db.query(Classe).filter(Classe.id_classe == classe_id).first()
    if not classe:
        raise HTTPException(status_code=404, detail="Classe introuvable")

    return classe

# ✅ Supprimer une classe
@router.delete("/supprimer_classe/{classe_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_class(
    classe_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Action réservée à l’administrateur")

    classe = db.query(Classe).filter(Classe.id_classe == classe_id).first()
    if not classe:
        raise HTTPException(status_code=404, detail="Classe introuvable")

    db.delete(classe)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ✅ Mettre à jour une classe
@router.put("/modifier_classe/{classe_id}", response_model=ClasseResponse)
async def update_class(
    classe_id: int,
    classe_update: ClasseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Action réservée à l’administrateur")

    classe = db.query(Classe).filter(Classe.id_classe == classe_id).first()
    if not classe:
        raise HTTPException(status_code=404, detail="Classe introuvable")

    classe.nom_classe = classe_update.nom_classe
    classe.niveau = classe_update.niveau
    classe.filiere = classe_update.filiere
    classe.annee_scolaire = classe_update.annee_scolaire
    classe.effectif = classe_update.effectif

    if classe_update.id_enseignant:
        enseignants = db.query(Enseignant).filter(Enseignant.id_enseignant.in_(classe_update.id_enseignant)).all()
        if not enseignants:
            raise HTTPException(status_code=404, detail="Enseignant introuvable")
        classe.enseignants = enseignants
    else:
        classe.enseignants = []

    db.commit()
    db.refresh(classe)
    return classe

#Assigner un enseignant à une classe
@router.post("/assigner_enseignant/{classe_id}/{enseignant_id}", response_model=ClasseResponse)
async def assign_teacher_to_class(
    classe_id: int,
    enseignant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Action réservée à l’administrateur")

    classe = db.query(Classe).filter(Classe.id_classe == classe_id).first()
    if not classe:
        raise HTTPException(status_code=404, detail="Classe introuvable")

    enseignant = db.query(Enseignant).filter(Enseignant.id_enseignant == enseignant_id).first()
    if not enseignant:
        raise HTTPException(status_code=404, detail="Enseignant introuvable")

    if enseignant in classe.enseignants:
        raise HTTPException(status_code=400, detail="L'enseignant est déjà assigné à cette classe")

    classe.enseignants.append(enseignant)
    db.commit()
    db.refresh(classe)
    return classe

#Retirer un enseignant d'une classe
@router.delete("/retirer_enseignant/{classe_id}/{enseignant_id}", response_model=ClasseResponse)
async def remove_teacher_from_class(
    classe_id: int,
    enseignant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Action réservée à l’administrateur")

    classe = db.query(Classe).filter(Classe.id_classe == classe_id).first()
    if not classe:
        raise HTTPException(status_code=404, detail="Classe introuvable")

    enseignant = db.query(Enseignant).filter(Enseignant.id_enseignant == enseignant_id).first()
    if not enseignant:
        raise HTTPException(status_code=404, detail="Enseignant introuvable")

    if enseignant not in classe.enseignants:
        raise HTTPException(status_code=400, detail="L'enseignant n'est pas assigné à cette classe")

    classe.enseignants.remove(enseignant)
    db.commit()
    db.refresh(classe)
    return classe

#Ajouter un étudiant à une classe
@router.post("/ajouter_etudiant/{classe_id}/{etudiant_id}", response_model=ClasseResponse)
async def add_student_to_class(
    classe_id: int,
    etudiant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Action réservée à l’administrateur")

    classe = db.query(Classe).filter(Classe.id_classe == classe_id).first()
    if not classe:
        raise HTTPException(status_code=404, detail="Classe introuvable")

    etudiant = db.query(Etudiant).filter(Etudiant.id_etudiant == etudiant_id).first()
    if not etudiant:
        raise HTTPException(status_code=404, detail="Étudiant introuvable")

    if etudiant.id_classe == classe.id_classe:
        raise HTTPException(status_code=400, detail="L'étudiant est déjà dans cette classe")

    etudiant.classe = classe

    db.commit()
    db.refresh(classe)
    return classe

#Retirer un étudiant d'une classe
@router.delete("/retirer_etudiant/{classe_id}/{etudiant_id}", response_model=ClasseResponse)
async def remove_student_from_class(
    classe_id: int,
    etudiant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Action réservée à l’administrateur")

    classe = db.query(Classe).filter(Classe.id_classe == classe_id).first()
    if not classe:
        raise HTTPException(status_code=404, detail="Classe introuvable")

    etudiant = db.query(Etudiant).filter(Etudiant.id_etudiant == etudiant_id).first()
    if not etudiant:
        raise HTTPException(status_code=404, detail="Étudiant introuvable")

    if etudiant.id_classe != classe.id_classe:
        raise HTTPException(status_code=400, detail="L'étudiant n'est pas dans cette classe")

    etudiant.classe = None

    db.commit()
    db.refresh(classe)
    return classe
