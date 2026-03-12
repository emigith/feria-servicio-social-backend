from app.core.db import SessionLocal
from app.models.period import Period
from app.models.opportunity import Opportunity


def run():
    db = SessionLocal()
    try:
        active_period = db.query(Period).filter(Period.is_active == True).first()

        if not active_period:
            print("No active period found. Create one first.")
            return

        existing = db.query(Opportunity).filter(Opportunity.period_id == active_period.id).first()
        if existing:
            print("Opportunities already exist for the active period.")
            return

        opportunities = [
            Opportunity(
                period_id=active_period.id,
                title="Apoyo en logística de eventos",
                description="Apoyo operativo durante actividades y eventos de servicio social.",
                company="Fundación Horizonte",
                location="CDMX",
                capacity=20,
                is_active=True,
            ),
            Opportunity(
                period_id=active_period.id,
                title="Tutoría académica comunitaria",
                description="Acompañamiento a estudiantes en sesiones de refuerzo académico.",
                company="Educa Más",
                location="Naucalpan",
                capacity=15,
                is_active=True,
            ),
        ]

        db.add_all(opportunities)
        db.commit()
        print("Seed de opportunities completado.")

    finally:
        db.close()


if __name__ == "__main__":
    run()