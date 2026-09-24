import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# En producción se puede sobreescribir con la variable de entorno DATABASE_URL
# (por ejemplo, para usar PostgreSQL en el entorno de prueba/despliegue).
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./donor_registry.db")

connect_args = (
    {"check_same_thread": False} if SQLALCHEMY_DATABASE_URL.startswith("sqlite") else {}
)

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Dependencia de FastAPI: entrega una sesión de BD y la cierra al terminar."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
