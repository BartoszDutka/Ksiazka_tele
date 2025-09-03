#!/usr/bin/env python3
"""
Migration script to make 'imie' and 'nazwisko' fields optional in contacts table.
This script updates the SQLite database schema to allow NULL values for name fields.
"""

import sqlite3
import sys
import os
from pathlib import Path

def migrate_database():
    """Migrate the database to make name fields optional"""
    
    # Get the database path
    db_path = Path(__file__).parent / "ksiazka_tele.db"
    
    if not db_path.exists():
        print(f"Database file not found: {db_path}")
        return False
    
    # Create backup
    backup_path = db_path.with_suffix('.db.backup')
    print(f"Creating backup: {backup_path}")
    
    import shutil
    shutil.copy2(db_path, backup_path)
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check current schema
        cursor.execute("PRAGMA table_info(kontakty)")
        columns = cursor.fetchall()
        print("Current schema:")
        for col in columns:
            print(f"  {col}")
        
        # SQLite doesn't support ALTER COLUMN directly, so we need to:
        # 1. Create new table with updated schema
        # 2. Copy data
        # 3. Drop old table
        # 4. Rename new table
        
        print("\nCreating new table with optional name fields...")
        
        # Create new table
        cursor.execute("""
            CREATE TABLE kontakty_new (
                id TEXT PRIMARY KEY,
                imie TEXT NULL,
                nazwisko TEXT NULL,
                numer_wewnetrzny TEXT NOT NULL UNIQUE,
                dzial TEXT,
                firma TEXT,
                notatki TEXT,
                created_at TIMESTAMP NOT NULL,
                updated_at TIMESTAMP NOT NULL
            )
        """)
        
        # Create indexes
        cursor.execute("CREATE INDEX ix_kontakty_new_numer_wewnetrzny ON kontakty_new (numer_wewnetrzny)")
        cursor.execute("CREATE INDEX ix_kontakty_new_dzial ON kontakty_new (dzial)")
        
        # Copy data from old table to new table
        cursor.execute("""
            INSERT INTO kontakty_new (
                id, imie, nazwisko, numer_wewnetrzny, dzial, firma, notatki, created_at, updated_at
            )
            SELECT 
                id, imie, nazwisko, numer_wewnetrzny, dzial, firma, notatki, created_at, updated_at
            FROM kontakty
        """)
        
        # Drop old table
        cursor.execute("DROP TABLE kontakty")
        
        # Rename new table
        cursor.execute("ALTER TABLE kontakty_new RENAME TO kontakty")
        
        # Commit changes
        conn.commit()
        
        # Verify the migration
        cursor.execute("PRAGMA table_info(kontakty)")
        columns = cursor.fetchall()
        print("\nNew schema:")
        for col in columns:
            print(f"  {col}")
        
        # Count records
        cursor.execute("SELECT COUNT(*) FROM kontakty")
        count = cursor.fetchone()[0]
        print(f"\nMigration completed successfully. {count} records migrated.")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"Migration failed: {e}")
        print(f"Restoring backup...")
        
        # Restore backup
        shutil.copy2(backup_path, db_path)
        return False

if __name__ == "__main__":
    print("Starting migration to make name fields optional...")
    
    if migrate_database():
        print("Migration completed successfully!")
        sys.exit(0)
    else:
        print("Migration failed!")
        sys.exit(1)
