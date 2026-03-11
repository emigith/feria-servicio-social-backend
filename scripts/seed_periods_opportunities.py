import sys
from pathlib import Path
from uuid import uuid4
from datetime import datetime, timezone

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.core.db import SessionLocal
from sqlalchemy import text


def main():
    db = SessionLocal()
    try:
        period_name = "2026_S1"

        existing_period = db.execute(
            text("SELECT id FROM periods WHERE name = :name"),
            {"name": period_name}
        ).fetchone()

        if existing_period:
            period_id = existing_period[0]
            print(f"Period already exists: {period_name}")
        else:
            period_id = str(uuid4())
            db.execute(
                text("""
                    INSERT INTO periods (id, name, starts_at, ends_at, is_active)
                    VALUES (:id, :name, :starts_at, :ends_at, :is_active)
                """),
                {
                    "id": period_id,
                    "name": period_name,
                    "starts_at": datetime(2026, 1, 10, tzinfo=timezone.utc),
                    "ends_at": datetime(2026, 6, 30, tzinfo=timezone.utc),
                    "is_active": True,
                }
            )
            print(f"Period created: {period_name}")

        opportunities = [
            {
                "id": str(uuid4()),
                "title": "Apoyo en logística social",
                "description": "Apoyo a coordinación de actividades y seguimiento de alumnos.",
                "company": "TEC CCM",
                "location": "CDMX",
                "capacity": 20,
                "is_active": True,
            },
            {
                "id": str(uuid4()),
                "title": "Soporte administrativo",
                "description": "Captura de información y apoyo en procesos internos.",
                "company": "Fundación Aliada",
                "location": "CDMX",
                "capacity": 15,
                "is_active": True,
            },
        ]

        created = 0

        for opp in opportunities:
            existing_opp = db.execute(
                text("SELECT id FROM opportunities WHERE title = :title"),
                {"title": opp["title"]}
            ).fetchone()

            if existing_opp:
                print(f"Opportunity already exists: {opp['title']}")
                continue

            db.execute(
                text("""
                    INSERT INTO opportunities
                    (id, period_id, title, description, company, location, capacity, is_active)
                    VALUES
                    (:id, :period_id, :title, :description, :company, :location, :capacity, :is_active)
                """),
                {
                    "id": opp["id"],
                    "period_id": period_id,
                    "title": opp["title"],
                    "description": opp["description"],
                    "company": opp["company"],
                    "location": opp["location"],
                    "capacity": opp["capacity"],
                    "is_active": opp["is_active"],
                }
            )
            created += 1

        db.commit()
        print(f"Seed completed. Opportunities created: {created}")

    except Exception as e:
        db.rollback()
        print(f"Error while seeding periods/opportunities: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()