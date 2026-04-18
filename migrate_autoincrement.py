#!/usr/bin/env python3
"""
Migration script to add AUTOINCREMENT to existing tables.
"""

import sqlite3
from datetime import datetime
import shutil

db_path = 'job_tracker.db'

# Backup the database first
backup_path = f'{db_path}.backup.{datetime.now().strftime("%Y%m%d_%H%M%S")}'
shutil.copy(db_path, backup_path)
print(f"✅ Backed up database to {backup_path}")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Define new schemas with AUTOINCREMENT
    migrations = [
        {
            'name': 'contacts',
            'new_schema': '''CREATE TABLE contacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company VARCHAR NOT NULL,
    firstname VARCHAR,
    lastname VARCHAR,
    linkedin_link VARCHAR,
    phone_number VARCHAR,
    updated_date DATE NOT NULL
)'''
        },
        {
            'name': 'job_offers',
            'new_schema': '''CREATE TABLE job_offers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company VARCHAR NOT NULL,
    title VARCHAR NOT NULL,
    url VARCHAR,
    date_added DATE NOT NULL
)'''
        },
        {
            'name': 'applications',
            'new_schema': '''CREATE TABLE applications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,
    client TEXT,
    job_link VARCHAR,
    date DATE NOT NULL,
    source VARCHAR NOT NULL,
    status VARCHAR NOT NULL,
    answer VARCHAR NOT NULL,
    answer_date DATE,
    expected_rate FLOAT,
    offered_rate FLOAT,
    duration VARCHAR,
    start_date DATE,
    notes VARCHAR,
    closed VARCHAR NOT NULL,
    my_decision TEXT DEFAULT "" NOT NULL,
    FOREIGN KEY (company_id) REFERENCES contacts(id)
)'''
        },
    ]

    for migration in migrations:
        table_name = migration['name']
        new_schema = migration['new_schema']

        print(f"\n🔄 Processing table: {table_name}")

        # Check if already has AUTOINCREMENT
        cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table_name}'")
        result = cursor.fetchone()
        if result and 'AUTOINCREMENT' in result[0]:
            print(f"   ℹ️  Already has AUTOINCREMENT")
            continue

        # Create new table
        temp_table = f"{table_name}_new"
        temp_schema = new_schema.replace(f'CREATE TABLE {table_name}', f'CREATE TABLE {temp_table}')
        cursor.execute(temp_schema)
        print(f"   ✓ Created {temp_table}")

        # Copy data
        cursor.execute(f"INSERT INTO {temp_table} SELECT * FROM {table_name}")
        rows = cursor.rowcount
        print(f"   ✓ Copied {rows} rows")

        # Drop old table
        cursor.execute(f"DROP TABLE {table_name}")
        print(f"   ✓ Dropped old {table_name}")

        # Rename new table
        cursor.execute(f"ALTER TABLE {temp_table} RENAME TO {table_name}")
        print(f"   ✅ {table_name} now has AUTOINCREMENT")

    conn.commit()
    print("\n✅ Migration completed successfully!")
    print("All tables now have AUTOINCREMENT - IDs will never be reused")

except Exception as e:
    conn.rollback()
    print(f"\n❌ Migration failed: {e}")
    print(f"Your backup is at: {backup_path}")
    raise

finally:
    conn.close()
