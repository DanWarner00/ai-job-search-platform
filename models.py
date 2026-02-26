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
    """User resume model (singleton)"""
    __tablename__ = 'resume'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255))
    filepath = db.Column(db.String(500))
    content = db.Column(db.Text)  # Parsed text content
    skills = db.Column(db.Text)  # JSON array
    experience = db.Column(db.Text)  # JSON array
    education = db.Column(db.Text)  # JSON array
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<Resume {self.filename}>'


class SearchPreferences(db.Model):
    """User's job search preferences"""
    __tablename__ = 'search_preferences'
    
    id = db.Column(db.Integer, primary_key=True)
    job_titles = db.Column(db.Text)  # Comma-separated or JSON
    keywords = db.Column(db.Text)  # Comma-separated or JSON
    search_description = db.Column(db.Text)  # Natural language description
    locations = db.Column(db.Text)  # Comma-separated locations
    min_salary = db.Column(db.Integer)
    max_salary = db.Column(db.Integer)
    remote_only = db.Column(db.Boolean, default=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<SearchPreferences {self.job_titles}>'


class Goal(db.Model):
    """Weekly goal tracking"""
    __tablename__ = 'goals'
    
    id = db.Column(db.Integer, primary_key=True)
    week_start_date = db.Column(db.Date, nullable=False, unique=True)
    target_applications = db.Column(db.Integer, default=10)
    actual_applications = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Goal week {self.week_start_date}: {self.actual_applications}/{self.target_applications}>'


class Email(db.Model):
    """Email tracking from Gmail"""
    __tablename__ = 'emails'
    
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey('applications.id'))
    gmail_message_id = db.Column(db.String(255), unique=True)
    subject = db.Column(db.Text)
    received_date = db.Column(db.DateTime)
    email_type = db.Column(db.String(50))  # interview_invite, rejection, followup
    processed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Email {self.email_type} for Application {self.application_id}>'
