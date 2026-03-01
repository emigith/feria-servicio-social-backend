1) Crea el archivo

En PowerShell (en la raíz del repo):

mkdir docs -ErrorAction SilentlyContinue
code .\docs\week2.md

Se te abre en VS Code. Pega esto:

# Semana 2 — Backend base + contratos JSON (Emilio)

## Objetivo
Dejar una base funcional del backend para:
- levantar API local con FastAPI/Uvicorn,
- estructurar el proyecto por capas,
- definir contratos JSON (schemas) visibles en Swagger,
- habilitar endpoints mínimos (health + auth estudiantes),
- dejar repo listo para colaborar (requirements + gitignore + commits).

---

## Repositorio
Backend: https://github.com/emigith/feria-servicio-social-backend

---

## Cómo correr (local)
> Requisitos: Python 3.x y Git instalados.

### 1) Clonar y abrir
```powershell
git clone https://github.com/emigith/feria-servicio-social-backend.git
cd feria-servicio-social-backend
code .
2) Crear y activar entorno virtual
python -m venv .venv
.\.venv\Scripts\Activate.ps1

Si PowerShell bloquea scripts:

Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
3) Instalar dependencias
python -m pip install -r requirements.txt
4) Levantar servidor
python -m uvicorn app.main:app --reload
URLs importantes

Swagger (OpenAPI): http://127.0.0.1:8000/docs

Health check: http://127.0.0.1:8000/api/v1/health

Endpoints disponibles (Semana 2)
Health

GET /api/v1/health
Response:

{ "ok": true }
Auth Estudiantes
Register

POST /api/v1/students/auth/register

Request:

{
  "matricula": "A01234567",
  "correo": "emilio@tec.mx",
  "password": "12345678",
  "nombre": "Emilio",
  "apellido": "Guillen"
}

Responses:

201 Created (registro exitoso)

409 Conflict:

{ "detail": "STUDENT_ALREADY_EXISTS" }

422 Validation Error (si no cumple schema)

Login

POST /api/v1/students/auth/login

Request:

{
  "matricula": "A01234567",
  "password": "12345678"
}

Response (ejemplo):

{
  "token": "JWT_HERE",
  "expiresIn": 3600
}
Estructura base del proyecto
app/
  main.py
  api/
    router.py
    routes/
      health.py
      auth_students.py
  core/
    config.py
    security.py
  schemas/
    auth.py
  services/
    auth_service.py
  repositories/
    student_repo.py
docs/
requirements.txt
.env.example
.gitignore
Notas técnicas relevantes

Se habilitó validación de contratos JSON con Pydantic (visible en Swagger).

Se corrigieron issues de entorno en Windows (ExecutionPolicy para activar .venv).

Se ignoraron archivos de caché (__pycache__, *.pyc) y entorno (.venv, .env) en .gitignore.