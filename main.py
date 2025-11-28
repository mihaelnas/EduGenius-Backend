from fastapi import FastAPI , Request 
from fastapi.responses import JSONResponse
from app.DB.database import Base, engine
from app.Route import etudiant, admin, refrech_token , classe, cours, enseignant , login , register, planning , ressource , matiere
from fastapi.middleware.cors import CORSMiddleware
from pydantic.error_wrappers import ValidationError
from dotenv import load_dotenv

load_dotenv()


app = FastAPI(title="FastAPI Users API")
Base.metadata.create_all(bind=engine)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,  
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "API is running"}


app.include_router(register.router, prefix="/users", tags=["Users"])
app.include_router(login.router, prefix="/auth", tags=["Authentication"])
app.include_router(refrech_token.router , prefix="/auth", tags=["Token Refresh"])
app.include_router(enseignant.router,prefix="/dashboard/enseignant", tags=["Enseignant"])
app.include_router(etudiant.router, prefix="/dashboard/etudiant", tags=["Etudiant"])
app.include_router(admin.router, prefix="/dashboard/admin", tags=["Admin"])
app.include_router(classe.router)
app.include_router(cours.router, prefix="/cours", tags=["Cours"])
app.include_router(planning.router, prefix="/planning", tags=["Planning"])
app.include_router(ressource.router, prefix="/cours", tags=["Ressources"])
app.include_router(matiere.router)
