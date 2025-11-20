#!/usr/bin/env python3
"""
Database migration: Add password reset token columns to users table
"""
import sqlite3
import os

# Path to database
DB_PATH = 'instance/supa_reports.db'

def migrate():
    """Add reset_token and reset_token_expires columns to users table"""

    if not os.path.exists(DB_PATH):
        print(f"❌ Database file not found: {DB_PATH}")
        return False

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(users)")
        columns = [col[1] for col in cursor.fetchall()]

        print("Current columns in users table:")
        for col in columns:
            print(f"  - {col}")
        print()

        # Add reset_token column if it doesn't exist
        if 'reset_token' not in columns:
            print("Adding reset_token column...")
            cursor.execute("""
                ALTER TABLE users
                ADD COLUMN reset_token VARCHAR(255)
            """)
            print("✓ Added reset_token column")
        else:
            print("✓ reset_token column already exists")

        # Add reset_token_expires column if it doesn't exist
        if 'reset_token_expires' not in columns:
            print("Adding reset_token_expires column...")
            cursor.execute("""
                ALTER TABLE users
                ADD COLUMN reset_token_expires DATETIME
            """)
            print("✓ Added reset_token_expires column")
        else:
            print("✓ reset_token_expires column already exists")

        conn.commit()
        print()
        print("=" * 60)
        print("✓ Migration completed successfully!")
        print("=" * 60)
        return True

    except Exception as e:
        conn.rollback()
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
