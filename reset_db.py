"""
Reset database with updated schema
Run this when you add new columns/tables to models.py
"""
from app import app, db
import os

# Path to database file
db_path = 'jobs.db'

print('🔄 Resetting database...')

# Delete old database if it exists
if os.path.exists(db_path):
    print(f'   Removing old database: {db_path}')
    os.remove(db_path)

# Create new database with updated schema
with app.app_context():
    print('   Creating tables...')
    db.create_all()
    print('✅ Database reset complete!')
    print('   All tables created with updated schema.')
    print(f'   Database: {db_path}')
