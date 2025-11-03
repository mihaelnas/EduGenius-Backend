from fastapi import FastAPI
from DB.database import Base, engine
from Route import etudiant, admin, refrech_token , classe, cours
from fastapi.middleware.cors import CORSMiddleware

from Route import enseignant, login, register

app = FastAPI()
Base.metadata.create_all(bind=engine)
app = FastAPI(title="FastAPI Users API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,  
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(register.router, prefix="/users", tags=["Users"])
app.include_router(login.router, prefix="/auth", tags=["Authentication"])
app.include_router(refrech_token.router , prefix="/auth", tags=["Token Refresh"])
app.include_router(enseignant.router,prefix="/dashboard/enseignant", tags=["Enseignant"])
app.include_router(etudiant.router, prefix="/dashboard/etudiant", tags=["Etudiant"])
app.include_router(admin.router, prefix="/dashboard/admin", tags=["Admin"])
app.include_router(classe.router, prefix="/classes", tags=["Classes"])
app.include_router(cours.router, prefix="/cours", tags=["Cours"])

