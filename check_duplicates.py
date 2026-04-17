#!/usr/bin/env python3
"""
Script to check for duplicate projects in the database.
Identifies projects with same title and period_id (which would indicate duplicate uploads).
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import all models to initialize relationships
from app.models.user import User
from app.models.student import Student
from app.models.period import Period
from app.models.opportunity import Opportunity
from app.models.enrollment import Enrollment
from app.models.otp_code import OtpCode
from app.models.checkin import Checkin

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://localhost/feriasocial")

# Create engine and session
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

try:
    # Query for duplicate projects (same title and period)
    duplicates = session.query(
        Opportunity.title,
        Opportunity.period_id,
        func.count(Opportunity.id).label('count')
    ).group_by(
        Opportunity.title,
        Opportunity.period_id
    ).having(
        func.count(Opportunity.id) > 1
    ).all()

    if duplicates:
        print(f"\nFound {len(duplicates)} groups of duplicate projects:\n")

        for title, period_id, count in duplicates:
            print(f"  Title: {title}")
            print(f"  Period ID: {period_id}")
            print(f"  Count: {count}")

            # Get period name
            period = session.query(Period).filter(Period.id == period_id).first()
            if period:
                print(f"  Period: {period.name}")

            # Get all instances of this duplicate
            projects = session.query(Opportunity).filter(
                Opportunity.title == title,
                Opportunity.period_id == period_id
            ).all()

            print(f"  Projects:")
            for p in projects:
                print(f"    - ID: {p.id}, Code: {p.project_code}, Company: {p.company}, Credit Hours: {p.credit_hours}")
            print()
    else:
        print("\nNo duplicate projects found!")

    # Also check for duplicate project codes within same period
    print("\n" + "="*60)
    print("Checking for duplicate project codes...\n")

    code_duplicates = session.query(
        Opportunity.project_code,
        Opportunity.period_id,
        func.count(Opportunity.id).label('count')
    ).filter(
        Opportunity.project_code != None
    ).group_by(
        Opportunity.project_code,
        Opportunity.period_id
    ).having(
        func.count(Opportunity.id) > 1
    ).all()

    if code_duplicates:
        print(f"Found {len(code_duplicates)} groups with duplicate codes:\n")

        for code, period_id, count in code_duplicates:
            print(f"  Code: {code}")
            print(f"  Period ID: {period_id}")
            print(f"  Count: {count}")

            period = session.query(Period).filter(Period.id == period_id).first()
            if period:
                print(f"  Period: {period.name}")

            projects = session.query(Opportunity).filter(
                Opportunity.project_code == code,
                Opportunity.period_id == period_id
            ).all()

            print(f"  Projects:")
            for p in projects:
                print(f"    - ID: {p.id}, Title: {p.title}, Company: {p.company}")
            print()
    else:
        print("No duplicate project codes found!")

finally:
    session.close()
