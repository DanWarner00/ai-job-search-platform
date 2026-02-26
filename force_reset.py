"""Force reset database"""
import os
import sys

db_file = 'jobs.db'

# Force delete
if os.path.exists(db_file):
    try:
        os.remove(db_file)
        print(f'✅ Deleted {db_file}')
    except Exception as e:
        print(f'❌ Error deleting: {e}')
        sys.exit(1)
else:
    print(f'⏭️  {db_file} does not exist')

# Create fresh database
print('Creating fresh database...')
from app import app, db

with app.app_context():
    db.create_all()
    print('✅ Database created successfully!')
    
    # Verify tables
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    
    print(f'\n📊 Created tables:')
    for table in tables:
        columns = inspector.get_columns(table)
        print(f'   - {table}')
        for col in columns:
            print(f'      • {col["name"]} ({col["type"]})')
    
    print(f'\n✅ All done! You can now start the app.')
