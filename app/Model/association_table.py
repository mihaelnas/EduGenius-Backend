# 🟢 Table d'association (many-to-many)
from sqlalchemy import Column, Integer, ForeignKey, Table
from DB.database import Base

enseignant_classe = Table(
    "enseignant_classe",
    Base.metadata,
    Column("id_enseignant", Integer, ForeignKey("enseignants.id_enseignant"), primary_key=True),
    Column("id_classe", Integer, ForeignKey("classes.id_classe"), primary_key=True)
)