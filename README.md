# API de Registro de Donantes

Módulo básico del sistema de gestión de donaciones de alimentos y recursos.
Implementa autenticación JWT, control de acceso por roles (`admin` / `usuario`)
y el registro/consulta de personas u organizaciones donantes.

Este módulo corresponde al punto **"Implementación y seguridad"** del reto final
de Ingeniería de Software (Tecmilenio).

## Stack

- **FastAPI** — framework web
- **SQLAlchemy** — ORM (SQLite por defecto, configurable vía `DATABASE_URL`)
- **python-jose** — generación/validación de JWT
- **bcrypt** — hashing de contraseñas
- **Pytest + pytest-cov** — pruebas unitarias y cobertura

## Ejecutar localmente

```bash
python -m venv venv
source venv/bin/activate        # En Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

La API queda disponible en `http://localhost:8000` y la documentación
interactiva (Swagger) en `http://localhost:8000/docs`.

## Ejecutar con Docker

```bash
docker build -t donor-api .
docker run -p 8000:8000 donor-api
```

## Endpoints

| Método | Ruta            | Rol requerido      | Descripción                              |
|--------|-----------------|---------------------|-------------------------------------------|
| GET    | `/health`       | Público             | Chequeo de salud del servicio             |
| POST   | `/auth/register`| Público             | Registra un usuario nuevo (rol `usuario`) |
| POST   | `/auth/login`   | Público             | Autentica y entrega un token JWT          |
| GET    | `/auth/me`      | Autenticado         | Datos del usuario actual                  |
| POST   | `/donors`       | Autenticado         | Registra un donante                       |
| GET    | `/donors`       | Autenticado         | Lista los donantes registrados            |
| GET    | `/donors/{id}`  | Autenticado         | Consulta un donante                       |
| DELETE | `/donors/{id}`  | **Admin**           | Elimina un donante                        |

> Nota: no existe un endpoint público para crear administradores (por diseño,
> para evitar escalación de privilegios). El primer admin se promueve
> directamente en la base de datos, tal como se hace en las pruebas
> (`tests/conftest.py`).

## Pruebas y cobertura

```bash
pytest --cov=app --cov-report=term-missing --cov-fail-under=80
```

Estado actual: **19 pruebas, ~97% de cobertura** sobre el paquete `app`.

## CI/CD (GitHub Actions)

El workflow en `.github/workflows/ci-cd.yml` corre en cada push/PR a `main`:

1. **test**: instala dependencias, corre la suite de Pytest y hace fallar el
   pipeline si la cobertura cae por debajo del 80 %.
2. **build-and-deploy** (solo si `test` pasa): construye la imagen Docker,
   la levanta como contenedor efímero (el "entorno de prueba"), verifica que
   `/health` responda, y publica la imagen en GitHub Container Registry
   (`ghcr.io`) usando el token automático del repositorio — no requiere
   configurar secretos adicionales.

## Variables de entorno

| Variable         | Descripción                                  | Valor por defecto              |
|------------------|-----------------------------------------------|----------------------------------|
| `DATABASE_URL`   | Cadena de conexión de la base de datos        | `sqlite:///./donor_registry.db` |
| `JWT_SECRET_KEY` | Clave secreta para firmar los JWT             | clave de desarrollo (cámbiala)  |
