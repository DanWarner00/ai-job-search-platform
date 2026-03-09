"""
Database models for Job Search Platform
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Job(db.Model):
    """Job posting model"""
    __tablename__ = 'jobs'
    
    id = db.Column(db.Integer, primary_key=True)
    source = db.Column(db.String(50), nullable=False)  # linkedin, indeed, ziprecruiter
    external_id = db.Column(db.String(255), nullable=False)  # job ID from source
    url = db.Column(db.Text, nullable=False)
    title = db.Column(db.String(255), nullable=False)
    company = db.Column(db.String(255))
    location = db.Column(db.String(255))
    salary_min = db.Column(db.Integer)
    salary_max = db.Column(db.Integer)
    description = db.Column(db.Text)
    requirements = db.Column(db.Text)
    posted_date = db.Column(db.DateTime)
    scraped_date = db.Column(db.DateTime, default=datetime.utcnow)
    match_score = db.Column(db.Integer)  # AI match score 0-100
    match_explanation = db.Column(db.Text)  # Why it matched
    starred = db.Column(db.Boolean, default=False)  # Pinned to top as reminder
    
    # Unique constraint
    __table_args__ = (db.UniqueConstraint('source', 'external_id', name='unique_job'),)
    
    # Relationship
    application = db.relationship('Application', backref='job', uselist=False, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Job {self.title} at {self.company}>'


class Application(db.Model):
    """Application tracking model"""
    __tablename__ = 'applications'
    
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'), nullable=False)
    status = db.Column(db.String(50), default='not_applied')  # not_applied, applied, interview, rejected, offer, not_interested (for AI learning)
    applied_date = db.Column(db.DateTime)
    rejection_reason = db.Column(db.String(255))  # not_qualified, low_pay, not_relevant, etc.
    notes = db.Column(db.Text)
    cover_letter = db.Column(db.Text)  # Generated cover letter
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    interviews = db.relationship('Interview', backref='application', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Application {self.status} for Job {self.job_id}>'


class Interview(db.Model):
    """Interview tracking model"""
    __tablename__ = 'interviews'
    
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey('applications.id'), nullable=False)
    scheduled_date = db.Column(db.DateTime)
    interview_type = db.Column(db.String(50))  # phone, video, onsite
    interviewer_name = db.Column(db.String(255))
    notes = db.Column(db.Text)
    outcome = db.Column(db.String(50))  # passed, rejected, waiting
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Interview {self.interview_type} for Application {self.application_id}>'


class Resume(db.Model):
    """User resume — one per search profile."""
    __tablename__ = 'resume'

    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('search_preferences.id', ondelete='SET NULL'), nullable=True)
    filename = db.Column(db.String(255))
    filepath = db.Column(db.String(500))
    content = db.Column(db.Text)  # Parsed text content
    skills = db.Column(db.Text)  # JSON array
    experience = db.Column(db.Text)  # JSON array
    education = db.Column(db.Text)  # JSON array
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<Resume {self.filename} profile={self.profile_id}>'


class SearchPreferences(db.Model):
    """User's job search preferences (one record per saved profile)"""
    __tablename__ = 'search_preferences'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), default='Default')  # Profile name
    is_active = db.Column(db.Boolean, default=True)  # Which profile is used for scraping
    job_titles = db.Column(db.Text)  # Comma-separated or JSON
    keywords = db.Column(db.Text)  # Comma-separated or JSON
    search_description = db.Column(db.Text)  # Natural language description of desired job
    work_experience = db.Column(db.Text)  # Additional work experience context for AI
    locations = db.Column(db.Text)  # Pipe-separated locations e.g. "Portland, OR|Salem, OR|Remote"
    min_salary = db.Column(db.Integer)
    max_salary = db.Column(db.Integer)
    remote_only = db.Column(db.Boolean, default=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    resume = db.relationship('Resume', foreign_keys='Resume.profile_id',
                             backref='profile', uselist=False)

    def get_locations_list(self):
        """Return locations as a list, supporting both pipe and comma separators."""
        if not self.locations:
            return []
        sep = '|' if '|' in self.locations else ','
        return [l.strip() for l in self.locations.split(sep) if l.strip()]

    def __repr__(self):
        return f'<SearchPreferences {self.name}: {self.job_titles}>'


