#!/usr/bin/env python3
"""
Initialize admin account for Supa Reports
Run this script once to create the admin account in your database.

Usage:
    python3 init_admin.py
"""
import os
from dotenv import load_dotenv
from flask import Flask
from models import db, User, UserStats

# Load environment variables
load_dotenv()

# Create Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///supa_reports.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)

def create_admin_account():
    """Create the admin account"""
    with app.app_context():
        # Create tables if they don't exist
        db.create_all()

        # Admin credentials
        admin_email = 'admin@supachat.global'
        admin_username = 'admin'
        admin_password = 'Admin@2024'  # CHANGE THIS PASSWORD AFTER FIRST LOGIN!

        # Check if admin already exists
        existing_admin = User.query.filter_by(email=admin_email).first()
        if existing_admin:
            print(f"✗ Admin account already exists: {admin_email}")
            print(f"   Username: {existing_admin.username}")
            print(f"   Is Admin: {existing_admin.is_admin}")
            print(f"   Verified: {existing_admin.verified}")
            return

        # Create admin user
        admin_user = User(
            email=admin_email,
            username=admin_username,
            verified=True,
            is_admin=True
        )
        admin_user.set_password(admin_password)

        db.session.add(admin_user)
        db.session.commit()

        # Create stats record for admin
        admin_stats = UserStats(user_id=admin_user.id)
        db.session.add(admin_stats)
        db.session.commit()

        print("=" * 70)
        print("✓ Admin account created successfully!")
        print("=" * 70)
        print(f"Email:    {admin_email}")
        print(f"Username: {admin_username}")
        print(f"Password: {admin_password}")
        print("=" * 70)
        print("IMPORTANT: Change this password immediately after first login!")
        print("=" * 70)

if __name__ == '__main__':
    create_admin_account()
