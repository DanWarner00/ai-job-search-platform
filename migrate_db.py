"""
Add missing columns to existing database and run db.create_all() for new tables.
"""
import sys
import os

# Flask uses the instance folder for SQLite — resolve it the same way
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app import app, db

instance_dir = app.instance_path
db_path = os.path.join(instance_dir, 'jobs.db')

import sqlite3

print(f'Migrating database at: {db_path}')

os.makedirs(instance_dir, exist_ok=True)

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # ── resume table columns ──────────────────────────────────────────────────
    for col, definition in [
        ('filepath', 'VARCHAR(500)'),
        ('uploaded_at', 'DATETIME'),
    ]:
        try:
            cursor.execute(f"ALTER TABLE resume ADD COLUMN {col} {definition}")
            print(f'   Added {col} to resume')
        except sqlite3.OperationalError as e:
            if 'duplicate column name' in str(e).lower():
                print(f'   {col} already exists in resume')
            else:
                raise

    # ── search_preferences columns ────────────────────────────────────────────
    for col, definition in [
        ('name',            'VARCHAR(100) DEFAULT "Default"'),
        ('is_active',       'BOOLEAN DEFAULT 1'),
        ('work_experience', 'TEXT'),
        ('user_id',         'INTEGER REFERENCES users(id)'),
    ]:
        try:
            cursor.execute(f"ALTER TABLE search_preferences ADD COLUMN {col} {definition}")
            print(f'   Added {col} to search_preferences')
        except sqlite3.OperationalError as e:
            if 'duplicate column name' in str(e).lower():
                print(f'   {col} already exists in search_preferences')
            else:
                raise

    # Ensure at least one preference is active
    cursor.execute("""
        UPDATE search_preferences SET is_active = 1
        WHERE id = (SELECT MIN(id) FROM search_preferences)
          AND NOT EXISTS (SELECT 1 FROM search_preferences WHERE is_active = 1)
    """)

    # ── jobs columns ─────────────────────────────────────────────────────────
    try:
        cursor.execute("ALTER TABLE jobs ADD COLUMN user_id INTEGER REFERENCES users(id)")
        print('   Added user_id to jobs')
    except sqlite3.OperationalError as e:
        if 'duplicate column name' in str(e).lower():
            print('   user_id already exists in jobs')
        else:
            raise

    # ── Fix unique constraint on jobs ─────────────────────────────────────────
    # Old constraint: (source, external_id) — breaks multi-user (second user scraping
    # same job hits a violation). New constraint: (source, external_id, user_id).
    # SQLite can't drop constraints directly; we recreate the table.
    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name='unique_job'")
        old_constraint = cursor.fetchone()
        if old_constraint:
            print('   Recreating jobs table to fix unique constraint (adding user_id)...')
            cursor.executescript("""
                BEGIN;
                CREATE TABLE jobs_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER REFERENCES users(id),
                    source VARCHAR(50) NOT NULL,
                    external_id VARCHAR(255) NOT NULL,
                    url TEXT NOT NULL,
                    title VARCHAR(255) NOT NULL,
                    company VARCHAR(255),
                    location VARCHAR(255),
                    salary_min INTEGER,
                    salary_max INTEGER,
                    description TEXT,
                    requirements TEXT,
                    posted_date DATETIME,
                    scraped_date DATETIME,
                    match_score INTEGER,
                    match_explanation TEXT,
                    starred BOOLEAN DEFAULT 0,
                    CONSTRAINT unique_job_per_user UNIQUE (source, external_id, user_id)
                );
                INSERT INTO jobs_new SELECT
                    id, user_id, source, external_id, url, title, company, location,
                    salary_min, salary_max, description, requirements, posted_date,
                    scraped_date, match_score, match_explanation,
                    COALESCE(starred, 0)
                FROM jobs;
                DROP TABLE jobs;
                ALTER TABLE jobs_new RENAME TO jobs;
                COMMIT;
            """)
            print('   Constraint fixed: unique_job_per_user (source, external_id, user_id)')
        else:
            print('   unique_job constraint already updated or not present')
    except Exception as e:
        print(f'   Could not update jobs constraint: {e}')

    conn.commit()
    conn.close()

    # ── create any missing tables (users, etc.) ───────────────────────────────
    with app.app_context():
        db.create_all()
        print('   Ensured all tables exist')

    print('Migration complete.')

except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()
