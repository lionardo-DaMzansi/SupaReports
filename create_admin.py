#!/usr/bin/env python3
"""
Create an admin user for Supa Reports
Usage: python3 create_admin.py
"""
from app import app
from models import db, User, UserStats
import getpass

def create_admin():
    with app.app_context():
        print("=" * 60)
        print("Create Admin User for Supa Reports")
        print("=" * 60)
        print()

        # Get user input
        email = input("Admin Email: ").strip().lower()
        username = input("Admin Username (optional, press Enter to use email): ").strip()
        password = getpass.getpass("Admin Password (min 8 chars): ")
        confirm_password = getpass.getpass("Confirm Password: ")

        # Validate
        if not email:
            print("❌ Email is required")
            return

        if len(password) < 8:
            print("❌ Password must be at least 8 characters")
            return

        if password != confirm_password:
            print("❌ Passwords do not match")
            return

        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            # Update existing user to admin
            existing_user.is_admin = True
            existing_user.verified = True
            db.session.commit()
            print()
            print("✅ Existing user updated to admin!")
            print(f"   Email: {email}")
            print(f"   Admin: True")
            print(f"   Verified: True")
        else:
            # Create new admin user
            admin = User(
                email=email,
                username=username or email.split('@')[0],
                verified=True,  # Auto-verify admin
                is_admin=True   # Set as admin
            )
            admin.set_password(password)

            db.session.add(admin)
            db.session.flush()

            # Create user stats
            stats = UserStats(user_id=admin.id)
            db.session.add(stats)

            db.session.commit()

            print()
            print("✅ Admin user created successfully!")
            print(f"   Email: {email}")
            print(f"   Username: {admin.username}")
            print(f"   Admin: True")
            print(f"   Verified: True")

        print()
        print("You can now login at: http://localhost:5173")
        print("=" * 60)

if __name__ == "__main__":
    try:
        create_admin()
    except KeyboardInterrupt:
        print("\n\nCancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
