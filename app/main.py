from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from . import auth, crud, models, schemas
from .database import engine, get_db

# Crea las tablas si no existen (para un entorno de prueba esto es suficiente;
# en producción se recomendaría usar migraciones con Alembic).
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API de Registro de Donantes",
    description=(
        "Módulo básico del sistema de gestión de donaciones: registro de personas "
        "donantes con autenticación JWT y control de acceso por roles (admin/usuario)."
    ),
    version="1.0.0",
)


@app.get("/health", tags=["Sistema"])
def health_check():
    return {"status": "ok"}


@app.post(
    "/auth/register",
    response_model=schemas.UserOut,
    status_code=status.HTTP_201_CREATED,
    tags=["Autenticación"],
)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    if crud.get_user_by_username(db, user.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El nombre de usuario ya está registrado",
        )
    return crud.create_user(db, user)


@app.post("/auth/login", response_model=schemas.Token, tags=["Autenticación"])
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_access_token(
        data={"sub": user.username, "role": user.role.value}
    )
    return schemas.Token(access_token=access_token)


@app.get("/auth/me", response_model=schemas.UserOut, tags=["Autenticación"])
def read_current_user(current_user: models.User = Depends(auth.get_current_user)):
    return current_user


@app.post(
    "/donors",
    response_model=schemas.DonorOut,
    status_code=status.HTTP_201_CREATED,
    tags=["Donantes"],
)
def create_donor(
    donor: schemas.DonorCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    return crud.create_donor(db, donor, created_by=current_user.id)


@app.get("/donors", response_model=list[schemas.DonorOut], tags=["Donantes"])
def list_donors(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    return crud.get_donors(db, skip, limit)


@app.get("/donors/{donor_id}", response_model=schemas.DonorOut, tags=["Donantes"])
def get_donor(
    donor_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    donor = crud.get_donor(db, donor_id)
    if not donor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Donante no encontrado"
        )
    return donor


@app.delete("/donors/{donor_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Donantes"])
def delete_donor(
    donor_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.require_admin),
):
    """Solo un administrador puede eliminar un registro de donante."""
    if not crud.delete_donor(db, donor_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Donante no encontrado"
        )
