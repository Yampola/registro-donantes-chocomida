import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import models
from app.database import Base, get_db
from app.main import app

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function", autouse=True)
def setup_database():
    """Crea tablas limpias antes de cada prueba y las tira al terminar."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture()
def client():
    return TestClient(app)


@pytest.fixture()
def user_token(client):
    """Registra y autentica un usuario con rol 'usuario' por defecto."""
    client.post("/auth/register", json={"username": "user1", "password": "userpass123"})
    resp = client.post("/auth/login", data={"username": "user1", "password": "userpass123"})
    return resp.json()["access_token"]


@pytest.fixture()
def admin_token(client):
    """Registra un usuario y lo promueve a 'admin' directamente en la BD de prueba."""
    client.post("/auth/register", json={"username": "admin1", "password": "adminpass123"})
    db = TestingSessionLocal()
    user = db.query(models.User).filter(models.User.username == "admin1").first()
    user.role = models.RoleEnum.admin
    db.commit()
    db.close()
    resp = client.post("/auth/login", data={"username": "admin1", "password": "adminpass123"})
    return resp.json()["access_token"]
