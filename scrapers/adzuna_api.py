"""
Adzuna API job scraper
Free API that aggregates jobs from Indeed, Monster, CareerBuilder, etc.

Get API keys: https://developer.adzuna.com/
"""
import requests
import os
from datetime import datetime
from .base import BaseScraper


class AdzunaAPIScraper(BaseScraper):
    """Scraper for Adzuna API"""
    
    def __init__(self):
        super().__init__()
        self.source = 'adzuna'
        self.app_id = os.getenv('ADZUNA_APP_ID')
        self.app_key = os.getenv('ADZUNA_APP_KEY')
        # Adzuna API format: /v1/api/jobs/{country}/search/{page}
        self.base_url = 'https://api.adzuna.com/v1/api/jobs/us/search'
    
    def parse_job_card(self, card):
        """Not used for API scraper - API returns JSON directly"""
        pass
    
    def scrape(self, keywords='', location='', max_results=50):
        """
        Scrape jobs from Adzuna API
        
        Args:
            keywords: Job search keywords (e.g., "Python Developer")
            location: Location (e.g., "Portland, OR")
            max_results: Maximum number of results to return
        
        Returns:
            list: List of job dictionaries
        """
        if not self.app_id or not self.app_key:
            print('❌ Adzuna API credentials not set. Add ADZUNA_APP_ID and ADZUNA_APP_KEY to .env')
            print('   Get free API keys: https://developer.adzuna.com/')
            return []
        
        jobs = []
        page = 1
        results_per_page = 50
        
        # Clean location - Adzuna prefers just city name or zip code
        # "Portland, OR" -> "Portland"
        clean_location = location.split(',')[0].strip() if location else ''
        
        print(f'🔍 Searching Adzuna API: {keywords} in {clean_location}')
        
        while len(jobs) < max_results:
            try:
                # Adzuna API format: /v1/api/jobs/us/search/{page}
                url = f'{self.base_url}/{page}'
                
                # Build API request - page is in URL, not params
                params = {
                    'app_id': self.app_id,
                    'app_key': self.app_key,
                    'results_per_page': min(results_per_page, max_results - len(jobs))
                }
                
                # Only add what/where if they have values
                if keywords:
                    params['what'] = keywords
                if clean_location:
                    params['where'] = clean_location
                
                response = requests.get(url, params=params, timeout=10)
                response.raise_for_status()
                data = response.json()
                
                if 'results' not in data or len(data['results']) == 0:
                    break
                
                # Parse results
                for job_data in data['results']:
                    try:
                        job = self._parse_job(job_data)
                        if job:
                            jobs.append(job)
                    except Exception as e:
                        print(f'   ⚠️  Error parsing job: {e}')
                        continue
                
                print(f'   Found {len(jobs)} jobs so far...')
                
                # Check if there are more pages
                if len(data['results']) < results_per_page:
                    break
                
                page += 1
                
            except requests.exceptions.RequestException as e:
                print(f'   ❌ API request error: {e}')
                break
            except Exception as e:
                print(f'   ❌ Error: {e}')
                break
        
        print(f'✅ Found {len(jobs)} jobs from Adzuna')
        return jobs[:max_results]
    
    def _parse_job(self, data):
        """Parse job data from Adzuna API response"""
        try:
            # Extract salary
            salary_min = data.get('salary_min')
            salary_max = data.get('salary_max')
            
            # Parse posted date
            posted_date = None
            if data.get('created'):
                try:
                    posted_date = datetime.fromisoformat(data['created'].replace('Z', '+00:00'))
                except:
                    pass
            
            # Build job object
            job = {
                'source': 'adzuna',
                'external_id': str(data['id']),
                'url': data['redirect_url'],
                'title': data['title'],
                'company': data.get('company', {}).get('display_name', 'Unknown'),
                'location': data.get('location', {}).get('display_name', ''),
                'salary_min': int(salary_min) if salary_min else None,
                'salary_max': int(salary_max) if salary_max else None,
                'description': data.get('description', ''),
                'requirements': None,  # Adzuna doesn't separate requirements
                'posted_date': posted_date
            }
            
            return job
            
        except Exception as e:
            print(f'Error parsing job: {e}')
            return None
