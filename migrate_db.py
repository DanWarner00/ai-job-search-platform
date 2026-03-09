"""
Add missing columns to existing database
"""
import sqlite3

db_path = 'jobs.db'

print('🔄 Migrating database...')

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Add filepath column to resume table if it doesn't exist
    try:
        cursor.execute("ALTER TABLE resume ADD COLUMN filepath VARCHAR(500)")
        print('   ✅ Added filepath column to resume table')
    except sqlite3.OperationalError as e:
        if 'duplicate column name' in str(e).lower():
            print('   ⏭️  filepath column already exists')
        else:
            raise
    
    # Add search_preferences table if it doesn't exist
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS search_preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_titles TEXT,
                keywords TEXT,
                search_description TEXT,
                locations TEXT,
                min_salary INTEGER,
                max_salary INTEGER,
                remote_only BOOLEAN,
                updated_at DATETIME
            )
        """)
        print('   ✅ Created search_preferences table')
    except Exception as e:
        print(f'   ⏭️  search_preferences table: {e}')
    
    # Fix resume.uploaded_date -> uploaded_at column name mismatch
    try:
        cursor.execute("SELECT uploaded_at FROM resume LIMIT 1")
        print('   ✅ uploaded_at column exists')
    except sqlite3.OperationalError:
        # Try to rename uploaded_date to uploaded_at
        try:
            cursor.execute("ALTER TABLE resume RENAME COLUMN uploaded_date TO uploaded_at")
            print('   ✅ Renamed uploaded_date to uploaded_at')
        except:
            print('   ⚠️  Could not rename uploaded_date column')
    
    # Add profile columns to search_preferences
    for col, definition in [
        ('name', 'VARCHAR(100) DEFAULT "Default"'),
        ('is_active', 'BOOLEAN DEFAULT 1'),
        ('work_experience', 'TEXT'),
    ]:
        try:
            cursor.execute(f"ALTER TABLE search_preferences ADD COLUMN {col} {definition}")
            print(f'   ✅ Added {col} column to search_preferences')
        except sqlite3.OperationalError as e:
            if 'duplicate column name' in str(e).lower():
                print(f'   ⏭️  {col} column already exists')
            else:
                raise

    # Set the first preference record as active if none are active
    try:
        cursor.execute("UPDATE search_preferences SET is_active = 1 WHERE id = (SELECT MIN(id) FROM search_preferences) AND NOT EXISTS (SELECT 1 FROM search_preferences WHERE is_active = 1)")
        print('   ✅ Ensured one active preference profile')
    except Exception as e:
        print(f'   ⚠️  Could not set active profile: {e}')

    conn.commit()
    conn.close()

    print('✅ Migration complete!')
    
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()
