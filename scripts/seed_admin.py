from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.core.security import hash_password
from app.models.organization import Organization
from app.models.user import User
from app.models.enums import OrgRole

def main():
    db: Session = SessionLocal()
    try:
        org_name = "Demo Org"
        email = "admin@example.com"
        password = "admin12345"

        org = db.query(Organization).filter(Organization.name == org_name).first()
        if not org:
            org = Organization(name=org_name)
            db.add(org)
            db.flush()

        user = db.query(User).filter(User.email == email).first()
        if not user:
            user = User(
                org_id=org.id,
                email=email,
                hashed_password=hash_password(password),
                role=OrgRole.admin.value,
            )
            db.add(user)

        db.commit()
        print("Seed complete.")
        print(f"Org: {org_name}")
        print(f"Admin: {email}")
        print(f"Password: {password}")
    finally:
        db.close()

if __name__ == "__main__":
    main()
