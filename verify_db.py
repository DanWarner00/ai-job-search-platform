"""Verify database setup"""
import os
import sqlite3

db_file = 'jobs.db'

if os.path.exists(db_file):
    print(f'✅ Database exists: {db_file}')
    print(f'   Size: {os.path.getsize(db_file)} bytes')
    
    # Check tables
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    print(f'\n📊 Tables in database:')
    for table in tables:
        print(f'   - {table[0]}')
        
        # Count rows
        cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
        count = cursor.fetchone()[0]
        print(f'     ({count} rows)')
    
    conn.close()
else:
    print(f'❌ Database not found: {db_file}')
    print('   Creating database...')
    
    from app import app, db
    with app.app_context():
        db.create_all()
    
    print('✅ Database created!')
