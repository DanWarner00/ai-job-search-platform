#!/usr/bin/env python3
"""
Reset database - Delete all jobs and applications, keep resume and preferences
"""
import os
from app import app
from models import db, Job, Application, Interview

print("🗑️  Resetting database...")
print("   This will delete all jobs and applications")
print("   Resume and search preferences will be kept")
print()

with app.app_context():
    # Count before
    job_count = Job.query.count()
    app_count = Application.query.count()
    interview_count = Interview.query.count()
    
    print(f"Current counts:")
    print(f"  - Jobs: {job_count}")
    print(f"  - Applications: {app_count}")
    print(f"  - Interviews: {interview_count}")
    print()
    
    # Delete all interviews first (foreign key constraint)
    Interview.query.delete()
    
    # Delete all applications
    Application.query.delete()
    
    # Delete all jobs
    Job.query.delete()
    
    # Commit
    db.session.commit()
    
    print("✅ Database reset complete!")
    print()
    print("Next steps:")
    print("  1. Make sure search preferences are set in Settings")
    print("  2. Run: flask scrape-jobs")
    print("  3. Run: flask calculate-matches")
    print()
