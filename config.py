"""
Application configuration
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///jobs.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # API Keys
    CLAUDE_API_KEY = os.getenv('CLAUDE_API_KEY')

    # Flask-Mail (for password reset emails)
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True') == 'True'
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER')

    # Scraping settings
    SCRAPE_FREQUENCY_HOURS = int(os.getenv('SCRAPE_FREQUENCY_HOURS', 24))
    MAX_JOBS_PER_BOARD = int(os.getenv('MAX_JOBS_PER_BOARD', 50))
    
    # Application settings
    JOBS_PER_PAGE = int(os.getenv('JOBS_PER_PAGE', 20))
    MIN_MATCH_SCORE = int(os.getenv('MIN_MATCH_SCORE', 60))
    
    # File uploads
    UPLOAD_FOLDER = 'static/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'pdf', 'docx'}


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False


# Config dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
