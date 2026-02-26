"""Recreate database from scratch"""
import os
import shutil

# Delete old database
if os.path.exists('jobs.db'):
    os.remove('jobs.db')
    print('✅ Deleted old database')

# Delete Python cache to ensure fresh imports
if os.path.exists('__pycache__'):
    shutil.rmtree('__pycache__')
    print('✅ Cleared cache')

# Import fresh and create database
print('Creating database with updated schema...')
from app import app, db
from models import Resume, SearchPreferences

with app.app_context():
    db.create_all()
    print('✅ Database created!')
    
    # Verify Resume table has correct columns
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    
    print('\n📋 Resume table columns:')
    columns = inspector.get_columns('resume')
    for col in columns:
        print(f'   - {col["name"]}: {col["type"]}')
    
    # Check if filepath exists
    column_names = [c['name'] for c in columns]
    if 'filepath' in column_names:
        print('\n✅ filepath column exists!')
    else:
        print('\n❌ filepath column MISSING!')
    
    if 'uploaded_at' in column_names:
        print('✅ uploaded_at column exists!')
    else:
        print('❌ uploaded_at column MISSING!')

print('\n✅ Done! Restart your Flask app now.')
