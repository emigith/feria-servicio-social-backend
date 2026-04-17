import csv
import io
import random
import re
import string
import unicodedata
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.opportunity import Opportunity
from app.repositories.user_repo import UserRepo


def _parse_modality(raw: str) -> str:
    """
    Convierte el código de modalidad del CSV a etiqueta legible.
    Ejemplos: 'CLIN | Proyecto Solidario Línea' → 'Remoto'
              'CLIP | Proyecto Solidario Mixto'  → 'Mixto'
              'PSP | Proyecto Solidario Presencial' → 'Presencial'
    """
    code = raw.strip()[:4].upper()
    if code.startswith("CLIN"):
        return "Remoto"
    if code.startswith("CLIP"):
        return "Mixto"
    if code.startswith("PSP"):
        return "Presencial"
    return "Presencial"


def _slugify(text: str, max_len: int = 30) -> str:
    """Convierte nombre de empresa en username válido (sin acentos, sin espacios)."""
    normalized = unicodedata.normalize("NFD", text)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", ascii_text).strip("_").lower()
    return slug[:max_len]


def _generate_password(length: int = 8) -> str:
    """Genera contraseña tipo SF-XXXX-YYYY."""
    chars = string.ascii_uppercase + string.digits
    part1 = "".join(random.choices(chars, k=4))
    part2 = "".join(random.choices(chars, k=4))
    return f"SF-{part1}-{part2}"


def _ensure_unique_username(base: str, existing: set[str]) -> str:
    """Si el username ya existe, agrega sufijo numérico."""
    candidate = base
    counter = 2
    while candidate in existing:
        candidate = f"{base[:27]}_{counter}"
        counter += 1
    return candidate


def load_csv_socioformadores(
    file_bytes: bytes,
    period_id: UUID,
    db: Session,
) -> list[dict]:
    """
    Lee el CSV de proyectos, agrupa por company, crea un usuario socioformador
    por empresa y crea todas sus oportunidades vinculadas.

    Retorna lista de credenciales: company, username, plain_password, projects_count.
    """
    content = file_bytes.decode("utf-8-sig", errors="replace")
    reader = csv.DictReader(io.StringIO(content))
    rows = list(reader)

    # Agrupar filas por company
    companies: dict[str, list[dict]] = {}
    for row in rows:
        company = row.get("company", "").strip()
        if not company:
            continue
        companies.setdefault(company, []).append(row)

    user_repo = UserRepo(db)
    used_usernames: set[str] = set()
    results: list[dict] = []

    for company, projects in companies.items():
        # Generar username único
        base_slug = _slugify(company)
        username = _ensure_unique_username(base_slug, used_usernames)
        used_usernames.add(username)

        # Verificar que el username no exista ya en la DB
        while user_repo.get_by_username(username):
            username = _ensure_unique_username(username + "_x", used_usernames)
            used_usernames.add(username)

        # Generar contraseña
        plain_pwd = _generate_password()
        hashed_pwd = hash_password(plain_pwd)

        # Crear usuario socioformador (flush sin commit aún)
        user = user_repo.create_socioformador(
            username=username,
            plain_password=plain_pwd,
            hashed_password=hashed_pwd,
        )

        # Crear oportunidades vinculadas
        for proj in projects:
            try:
                capacity = int(proj.get("capacity", 10))
            except ValueError:
                capacity = 10

            try:
                credit_hours = int(proj.get("credit_hours") or 0) or None
            except ValueError:
                credit_hours = None

            is_active_raw = proj.get("is_active", "TRUE").strip().upper()
            is_active = is_active_raw in ("TRUE", "1", "YES", "SI")

            raw_code = (proj.get("id") or "").strip()[:30] or None

            opp = Opportunity(
                period_id=period_id,
                partner_user_id=user.id,
                project_code=raw_code,
                title=(proj.get("title") or "Sin título").strip()[:150],
                company=company[:150],
                description=(proj.get("description") or "").strip() or None,
                location=(proj.get("location") or "").strip()[:150] or None,
                modality=_parse_modality(proj.get("modality") or ""),
                capacity=capacity,
                credit_hours=credit_hours,
                is_active=is_active,
            )
            db.add(opp)

        results.append({
            "company": company,
            "username": username,
            "plain_password": plain_pwd,
            "projects_count": len(projects),
        })

    db.commit()
    return results
