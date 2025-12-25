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

        # Create organization
        org = db.query(Organization).filter(Organization.name == org_name).first()
        if not org:
            org = Organization(name=org_name)
            db.add(org)
            db.flush()

        # Define test users with different roles
        users = [
            {
                "email": "admin@example.com",
                "password": "admin12345",
                "role": OrgRole.admin.value,
            },
            {
                "email": "editor@example.com",
                "password": "editor12345",
                "role": OrgRole.editor.value,
            },
            {
                "email": "viewer@example.com",
                "password": "viewer12345",
                "role": OrgRole.viewer.value,
            },
        ]

        # Create or update each user
        for user_data in users:
            user = db.query(User).filter(User.email == user_data["email"]).first()
            if not user:
                user = User(
                    org_id=org.id,
                    email=user_data["email"],
                    hashed_password=hash_password(user_data["password"]),
                    role=user_data["role"],
                )
                db.add(user)
            else:
                # Update existing user to ensure correct org, password, and role
                user.org_id = org.id
                user.hashed_password = hash_password(user_data["password"])
                user.role = user_data["role"]

        db.commit()
        print("Seed complete.")
        print(f"Org: {org_name}")
        print("\nTest users (created/updated):")
        for user_data in users:
            print(f"  - {user_data['role']}: {user_data['email']} / {user_data['password']}")
    finally:
        db.close()

if __name__ == "__main__":
    main()
