"""
Base scraper class for job boards
"""
from abc import ABC, abstractmethod
from datetime import datetime
import requests
from bs4 import BeautifulSoup


class BaseScraper(ABC):
    """Abstract base class for job scrapers"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.jobs = []
    
    @abstractmethod
    def scrape(self, keywords='python', location='Portland, OR', max_results=50):
        """
        Scrape jobs from the board
        
        Args:
            keywords: Job search keywords
            location: Job location
            max_results: Maximum number of jobs to scrape
            
        Returns:
            List of job dictionaries
        """
        pass
    
    @abstractmethod
    def parse_job_card(self, card):
        """
        Parse a single job card/listing
        
        Args:
            card: BeautifulSoup element of job card
            
        Returns:
            Dictionary with job data
        """
        pass
    
    def clean_salary(self, salary_text):
        """Extract salary range from text"""
        if not salary_text:
            return None, None
        
        # Extract numbers from salary text
        import re
        numbers = re.findall(r'\$?([\d,]+)k?', salary_text.lower())
        
        if len(numbers) >= 2:
            try:
                min_sal = int(numbers[0].replace(',', ''))
                max_sal = int(numbers[1].replace(',', ''))
                
                # Handle 'k' notation
                if 'k' in salary_text.lower():
                    min_sal *= 1000
                    max_sal *= 1000
                
                return min_sal, max_sal
            except:
                return None, None
        
        return None, None
    
    def parse_date(self, date_str):
        """Parse relative date strings like '2 days ago'"""
        if not date_str:
            return None
        
        from dateutil.relativedelta import relativedelta
        import re
        
        today = datetime.now()
        
        # Handle "today", "just posted", etc.
        if 'today' in date_str.lower() or 'just posted' in date_str.lower():
            return today
        
        # Handle "X days ago"
        match = re.search(r'(\d+)\s*(day|hour|minute)', date_str.lower())
        if match:
            value = int(match.group(1))
            unit = match.group(2)
            
            if 'day' in unit:
                return today - relativedelta(days=value)
            elif 'hour' in unit:
                return today - relativedelta(hours=value)
            elif 'minute' in unit:
                return today - relativedelta(minutes=value)
        
        return None
    
    def save_jobs(self):
        """Save scraped jobs to database"""
        from models import db, Job
        from datetime import datetime
        
        saved_count = 0
        
        for job_data in self.jobs:
            # Check if job already exists
            existing = Job.query.filter_by(
                source=job_data['source'],
                external_id=job_data['external_id']
            ).first()
            
            if existing:
                continue
            
            # Create new job
            job = Job(
                source=job_data['source'],
                external_id=job_data['external_id'],
                url=job_data['url'],
                title=job_data['title'],
                company=job_data.get('company'),
                location=job_data.get('location'),
                salary_min=job_data.get('salary_min'),
                salary_max=job_data.get('salary_max'),
                description=job_data.get('description'),
                requirements=job_data.get('requirements'),
                posted_date=job_data.get('posted_date'),
                scraped_date=datetime.utcnow()
            )
            
            db.session.add(job)
            saved_count += 1
        
        db.session.commit()
        return saved_count
