"""
Job Search Platform - Main Application
"""
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from config import config
from models import db, Job, Application, Interview, Resume, Goal, Email, SearchPreferences
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import os

# Initialize Flask app
app = Flask(__name__)

# Load config
env = os.getenv('FLASK_ENV', 'development')
app.config.from_object(config[env])

# Initialize database
db.init_app(app)

# Create upload folder
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


# Context processor to make resume/prefs available to all templates
@app.context_processor
def inject_global_context():
    resume = Resume.query.first()
    prefs = SearchPreferences.query.first()
    return {
        'has_resume': resume is not None,
        'has_preferences': prefs is not None and bool(prefs.job_titles),
        'resume': resume,
        'preferences': prefs
    }


# Routes
@app.route('/')
def index():
    """Main dashboard - job listings"""
    # Get filter parameters
    min_score = request.args.get('min_score', 0, type=int)
    max_score = request.args.get('max_score', 100, type=int)
    location = request.args.get('location', '')
    source = request.args.get('source', '')
    page = request.args.get('page', 1, type=int)
    sort_by = request.args.get('sort_by', 'match')  # match, posted, scraped
    
    # Query jobs
    query = Job.query.filter(
        Job.match_score >= min_score,
        Job.match_score <= max_score
    )
    
    if location:
        query = query.filter(Job.location.like(f'%{location}%'))
    
    if source:
        query = query.filter(Job.source == source)
    
    # Order by selected sort
    if sort_by == 'posted':
        query = query.order_by(Job.posted_date.desc().nullslast())
    elif sort_by == 'scraped':
        query = query.order_by(Job.scraped_date.desc())
    else:  # match (default)
        query = query.order_by(Job.match_score.desc(), Job.posted_date.desc().nullslast())
    
    # Paginate
    jobs = query.paginate(page=page, per_page=app.config['JOBS_PER_PAGE'], error_out=False)
    
    # Get stats for header
    stats = {
        'total_jobs': Job.query.count(),
        'applied': Application.query.filter_by(status='applied').count(),
        'interviews': Application.query.filter_by(status='interview').count(),
        'high_match': Job.query.filter(Job.match_score >= 80).count()
    }
    
    # Get source breakdown for debugging
    source_counts = db.session.query(Job.source, db.func.count(Job.id)).group_by(Job.source).all()
    source_stats = {source: count for source, count in source_counts}
    
    return render_template('index.html', jobs=jobs, stats=stats, 
                         min_score=min_score, max_score=max_score, 
                         location=location, source=source, sort_by=sort_by,
                         source_stats=source_stats)


@app.route('/job/<int:job_id>')
def job_detail(job_id):
    """Job detail page"""
    job = Job.query.get_or_404(job_id)
    application = Application.query.filter_by(job_id=job_id).first()
    
    return render_template('job_detail.html', job=job, application=application)


@app.route('/applications')
def applications():
    """Application tracker (Kanban board)"""
    # Calculate date 3 weeks ago
    three_weeks_ago = datetime.utcnow() - timedelta(weeks=3)
    
    not_applied = Job.query.outerjoin(Application).filter(
        (Application.id == None) | (Application.status == 'not_applied')
    ).order_by(Job.match_score.desc()).limit(50).all()
    
    # Applied but not moved to inactive yet (less than 3 weeks old)
    applied = Application.query.filter_by(status='applied').filter(
        Application.applied_date > three_weeks_ago
    ).order_by(
        Application.applied_date.desc()
    ).all()
    
    # Inactive: applied more than 3 weeks ago with no response
    inactive = Application.query.filter_by(status='applied').filter(
        Application.applied_date <= three_weeks_ago
    ).order_by(
        Application.applied_date.desc()
    ).all()
    
    interviews = Application.query.filter_by(status='interview').order_by(
        Application.applied_date.desc()
    ).all()
    
    rejected = Application.query.filter_by(status='rejected').order_by(
        Application.updated_at.desc()
    ).all()
    
    # Not Interested - jobs user explicitly marked as not relevant
    not_interested = Application.query.filter_by(status='not_interested').order_by(
        Application.updated_at.desc()
    ).all()
    
    return render_template('applications.html',
                         not_applied=not_applied,
                         applied=applied,
                         interviews=interviews,
                         rejected=rejected,
                         inactive=inactive,
                         not_interested=not_interested)


@app.route('/calendar')
def calendar():
    """Calendar view for interviews"""
    from calendar import monthcalendar, month_name
    from datetime import datetime
    
    # Get current month/year or from query params
    now = datetime.now()
    year = request.args.get('year', now.year, type=int)
    month = request.args.get('month', now.month, type=int)
    
    # Get interviews for this month
    from datetime import date
    start_date = date(year, month, 1)
    if month == 12:
        end_date = date(year + 1, 1, 1)
    else:
        end_date = date(year, month + 1, 1)
    
    interviews = Interview.query.filter(
        Interview.scheduled_date >= start_date,
        Interview.scheduled_date < end_date
    ).all()
    
    # Group interviews by date
    interviews_by_date = {}
    for interview in interviews:
        date_key = interview.scheduled_date.date() if interview.scheduled_date else None
        if date_key:
            if date_key not in interviews_by_date:
                interviews_by_date[date_key] = []
            interviews_by_date[date_key].append(interview)
    
    # Get calendar grid
    cal = monthcalendar(year, month)
    
    # Calculate prev/next month
    if month == 1:
        prev_month, prev_year = 12, year - 1
    else:
        prev_month, prev_year = month - 1, year
    
    if month == 12:
        next_month, next_year = 1, year + 1
    else:
        next_month, next_year = month + 1, year
    
    # Get upcoming interviews (all future interviews)
    upcoming_interviews = Interview.query.join(Application).filter(
        Interview.scheduled_date >= now
    ).order_by(Interview.scheduled_date).limit(10).all()
    
    return render_template('calendar.html',
                         calendar=cal,
                         month=month,
                         month_name=month_name[month],
                         year=year,
                         interviews_by_date=interviews_by_date,
                         today=now.date(),
                         prev_month=prev_month,
                         prev_year=prev_year,
                         next_month=next_month,
                         next_year=next_year,
                         upcoming_interviews=upcoming_interviews)


@app.route('/analytics')
def analytics():
    """Analytics dashboard"""
    # Calculate stats
    total_viewed = Job.query.count()
    total_applied = Application.query.filter(
        Application.status.in_(['applied', 'interview', 'rejected', 'offer'])
    ).count()
    total_interviews = Application.query.filter_by(status='interview').count()
    total_offers = Application.query.filter_by(status='offer').count()
    
    stats = {
        'viewed': total_viewed,
        'applied': total_applied,
        'interviews': total_interviews,
        'offers': total_offers
    }
    
    return render_template('analytics.html', stats=stats)


@app.route('/upload-resume', methods=['POST'])
def upload_resume():
    """Handle resume upload"""
    if 'resume' not in request.files:
        flash('No file selected', 'error')
        return redirect(url_for('index'))
    
    file = request.files['resume']
    
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('index'))
    
    # Check file extension
    allowed_extensions = {'pdf', 'docx'}
    if not ('.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
        flash('Invalid file type. Please upload PDF or DOCX', 'error')
        return redirect(url_for('index'))
    
    # Save file
    filename = secure_filename(file.filename)
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    new_filename = f"resume_{timestamp}.{filename.rsplit('.', 1)[1].lower()}"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)
    file.save(filepath)
    
    # Update or create resume record
    resume = Resume.query.first()
    if not resume:
        resume = Resume()
        db.session.add(resume)
    
    resume.filename = new_filename
    resume.filepath = filepath
    resume.uploaded_at = datetime.utcnow()
    
    # TODO: Parse resume and extract text/skills using AI
    
    db.session.commit()
    
    flash('Resume uploaded successfully! AI matching will be enabled once resume is parsed.', 'success')
    return redirect(url_for('index'))


@app.route('/api/application/update', methods=['POST'])
def update_application():
    """Update application status"""
    data = request.get_json()
    job_id = data.get('job_id')
    status = data.get('status')
    rejection_reason = data.get('rejection_reason', '')
    notes = data.get('notes', '')
    
    # Get or create application
    application = Application.query.filter_by(job_id=job_id).first()
    
    if not application:
        application = Application(job_id=job_id)
        db.session.add(application)
    
    application.status = status
    application.rejection_reason = rejection_reason
    application.notes = notes
    
    if status == 'applied':
        from datetime import datetime
        application.applied_date = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Application updated'})


@app.route('/settings')
def settings():
    """Settings page for resume and search preferences"""
    resume = Resume.query.first()
    prefs = SearchPreferences.query.first()
    
    return render_template('settings.html', resume=resume, prefs=prefs)


@app.route('/test-cover-letter')
def test_cover_letter():
    """Test page for cover letter API"""
    return render_template('test_cover_letter.html')


@app.route('/api/preferences/update', methods=['POST'])
def update_preferences():
    """Update search preferences"""
    data = request.get_json()
    
    prefs = SearchPreferences.query.first()
    if not prefs:
        prefs = SearchPreferences()
        db.session.add(prefs)
    
    prefs.job_titles = data.get('job_titles', '')
    prefs.keywords = data.get('keywords', '')
    prefs.search_description = data.get('search_description', '')
    prefs.locations = data.get('locations', 'Portland, OR')
    prefs.min_salary = data.get('min_salary')
    prefs.max_salary = data.get('max_salary')
    prefs.remote_only = data.get('remote_only', False)
    
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Preferences updated successfully'})


@app.route('/api/scrape/indeed', methods=['POST'])
def scrape_indeed():
    """Scrape jobs from Indeed only"""
    try:
        from scrapers.indeed_playwright import IndeedPlaywrightScraper as IndeedScraper
    except ImportError:
        return jsonify({
            'success': False,
            'message': 'Indeed scraper not available (Playwright not installed)'
        }), 400
    
    from ai.resume_parser import parse_resume
    from ai.job_matcher import calculate_match_score
    
    # Get search preferences
    prefs = SearchPreferences.query.first()
    
    if not prefs or not prefs.job_titles:
        return jsonify({
            'success': False, 
            'message': 'Please set search preferences first (job titles required)'
        }), 400
    
    # Get resume for AI matching
    resume = Resume.query.first()
    resume_text = None
    if resume and resume.filepath:
        resume_text = parse_resume(resume.filepath)
    
    # Parse job titles and locations
    job_titles = [t.strip() for t in prefs.job_titles.split(',') if t.strip()]
    locations = [l.strip() for l in (prefs.locations or 'Portland, OR').split(',') if l.strip()]
    
    total_saved = 0
    total_duplicates = 0
    
    try:
        for title in job_titles[:2]:  # Limit to 2 titles
            for location in locations[:1]:  # Limit to 1 location
                scraper = IndeedScraper()
                jobs = scraper.scrape(keywords=title, location=location, max_results=25)
                
                if not jobs:
                    continue
                
                # Save jobs to database
                for job_data in jobs:
                    try:
                        # Check if job already exists
                        existing = Job.query.filter_by(
                            source=job_data['source'],
                            external_id=job_data['external_id']
                        ).first()
                        
                        if existing:
                            total_duplicates += 1
                            continue
                        
                        # Create new job
                        job = Job(
                            source=job_data['source'],
                            external_id=job_data['external_id'],
                            url=job_data['url'],
                            title=job_data['title'],
                            company=job_data['company'],
                            location=job_data['location'],
                            salary_min=job_data.get('salary_min'),
                            salary_max=job_data.get('salary_max'),
                            description=job_data['description'],
                            requirements=job_data.get('requirements'),
                            posted_date=job_data.get('posted_date'),
                            scraped_date=datetime.utcnow(),
                            match_score=75  # Temporary - will calculate below
                        )
                        
                        db.session.add(job)
                        db.session.flush()  # Get the job ID
                        
                        # Calculate real match score with AI if resume available
                        if resume_text:
                            try:
                                match_score, explanation = calculate_match_score(resume_text, job)
                                job.match_score = match_score
                                job.match_explanation = explanation
                            except Exception as e:
                                print(f'Error calculating match score: {e}')
                                job.match_score = 75  # Fallback to placeholder
                                job.match_explanation = None
                        
                        total_saved += 1
                        
                    except Exception as e:
                        print(f'Error saving job: {e}')
                        continue
                
                db.session.commit()
        
        if resume_text:
            message = f'Indeed: Found {total_saved} new jobs with AI match scores ({total_duplicates} duplicates skipped)'
        else:
            message = f'Indeed: Found {total_saved} new jobs ({total_duplicates} duplicates skipped). Upload resume for AI match scores.'
        
        return jsonify({
            'success': True,
            'message': message,
            'saved': total_saved,
            'duplicates': total_duplicates,
            'source': 'indeed'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Indeed error: {str(e)}'
        }), 500


@app.route('/api/scrape/adzuna', methods=['POST'])
def scrape_adzuna():
    """Scrape jobs from Adzuna API only"""
    from scrapers.adzuna_api import AdzunaAPIScraper
    from ai.resume_parser import parse_resume
    from ai.job_matcher import calculate_match_score
    
    # Get search preferences
    prefs = SearchPreferences.query.first()
    
    if not prefs or not prefs.job_titles:
        return jsonify({
            'success': False, 
            'message': 'Please set search preferences first (job titles required)'
        }), 400
    
    # Get resume for AI matching
    resume = Resume.query.first()
    resume_text = None
    if resume and resume.filepath:
        resume_text = parse_resume(resume.filepath)
    
    # Parse job titles and locations
    job_titles = [t.strip() for t in prefs.job_titles.split(',') if t.strip()]
    locations = [l.strip() for l in (prefs.locations or 'Portland, OR').split(',') if l.strip()]
    
    total_saved = 0
    total_duplicates = 0
    
    try:
        for title in job_titles[:2]:  # Limit to 2 titles
            for location in locations[:1]:  # Limit to 1 location
                scraper = AdzunaAPIScraper()
                jobs = scraper.scrape(keywords=title, location=location, max_results=25)
                
                if not jobs:
                    continue
                
                # Save jobs to database
                for job_data in jobs:
                    try:
                        # Check if job already exists
                        existing = Job.query.filter_by(
                            source=job_data['source'],
                            external_id=job_data['external_id']
                        ).first()
                        
                        if existing:
                            total_duplicates += 1
                            continue
                        
                        # Create new job
                        job = Job(
                            source=job_data['source'],
                            external_id=job_data['external_id'],
                            url=job_data['url'],
                            title=job_data['title'],
                            company=job_data['company'],
                            location=job_data['location'],
                            salary_min=job_data.get('salary_min'),
                            salary_max=job_data.get('salary_max'),
                            description=job_data['description'],
                            requirements=job_data.get('requirements'),
                            posted_date=job_data.get('posted_date'),
                            scraped_date=datetime.utcnow(),
                            match_score=75  # Temporary - will calculate below
                        )
                        
                        db.session.add(job)
                        db.session.flush()  # Get the job ID
                        
                        # Calculate real match score with AI if resume available
                        if resume_text:
                            try:
                                match_score, explanation = calculate_match_score(resume_text, job)
                                job.match_score = match_score
                                job.match_explanation = explanation
                            except Exception as e:
                                print(f'Error calculating match score: {e}')
                                job.match_score = 75  # Fallback to placeholder
                                job.match_explanation = None
                        
                        total_saved += 1
                        
                    except Exception as e:
                        print(f'Error saving job: {e}')
                        continue
                
                db.session.commit()
        
        if resume_text:
            message = f'Adzuna: Found {total_saved} new jobs with AI match scores ({total_duplicates} duplicates skipped)'
        else:
            message = f'Adzuna: Found {total_saved} new jobs ({total_duplicates} duplicates skipped). Upload resume for AI match scores.'
        
        return jsonify({
            'success': True,
            'message': message,
            'saved': total_saved,
            'duplicates': total_duplicates,
            'source': 'adzuna'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Adzuna error: {str(e)}'
        }), 500


@app.route('/api/scrape/run', methods=['POST'])
def run_scraper():
    """Run job scraper via API (for UI button) - DEPRECATED, use specific endpoints"""
    from scrapers.adzuna_api import AdzunaAPIScraper
    
    # Build list of available scrapers
    scrapers = []
    try:
        from scrapers.indeed_playwright import IndeedPlaywrightScraper as IndeedScraper
        scrapers.append(('Indeed', IndeedScraper))
    except ImportError:
        pass
    
    # Always add Adzuna (API-based, no dependencies)
    scrapers.append(('Adzuna', AdzunaAPIScraper))
    
    from ai.resume_parser import parse_resume
    from ai.job_matcher import calculate_match_score
    
    # Get search preferences
    prefs = SearchPreferences.query.first()
    
    if not prefs or not prefs.job_titles:
        return jsonify({
            'success': False, 
            'message': 'Please set search preferences first (job titles required)'
        }), 400
    
    # Get resume for AI matching
    resume = Resume.query.first()
    resume_text = None
    if resume and resume.filepath:
        resume_text = parse_resume(resume.filepath)
    
    # Parse job titles and locations
    job_titles = [t.strip() for t in prefs.job_titles.split(',') if t.strip()]
    locations = [l.strip() for l in (prefs.locations or 'Portland, OR').split(',') if l.strip()]
    
    total_saved = 0
    total_duplicates = 0
    errors = []
    
    try:
        # Loop through all scrapers
        for scraper_name, ScraperClass in scrapers:
            for title in job_titles[:2]:  # Limit to 2 titles via API to avoid long waits
                for location in locations[:1]:  # Limit to 1 location
                    try:
                        scraper = ScraperClass()
                        jobs = scraper.scrape(keywords=title, location=location, max_results=25)
                        
                        if not jobs:
                            continue
                        
                        # Save jobs to database
                        for job_data in jobs:
                            try:
                                # Check if job already exists
                                existing = Job.query.filter_by(
                                    source=job_data['source'],
                                    external_id=job_data['external_id']
                                ).first()
                                
                                if existing:
                                    total_duplicates += 1
                                    continue
                                
                                # Create new job
                                job = Job(
                                    source=job_data['source'],
                                    external_id=job_data['external_id'],
                                    url=job_data['url'],
                                    title=job_data['title'],
                                    company=job_data['company'],
                                    location=job_data['location'],
                                    salary_min=job_data.get('salary_min'),
                                    salary_max=job_data.get('salary_max'),
                                    description=job_data['description'],
                                    requirements=job_data.get('requirements'),
                                    posted_date=job_data.get('posted_date'),
                                    scraped_date=datetime.utcnow(),
                                    match_score=75  # Temporary - will calculate below
                                )
                                
                                db.session.add(job)
                                db.session.flush()  # Get the job ID
                                
                                # Calculate real match score with AI if resume available
                                if resume_text:
                                    try:
                                        match_score, explanation = calculate_match_score(resume_text, job)
                                        job.match_score = match_score
                                        job.match_explanation = explanation
                                    except Exception as e:
                                        print(f'Error calculating match score: {e}')
                                        job.match_score = 75  # Fallback to placeholder
                                        job.match_explanation = None
                                
                                total_saved += 1
                                
                            except Exception as e:
                                print(f'Error saving job: {e}')
                                continue
                        
                        db.session.commit()
                        
                    except Exception as e:
                        error_msg = f'{scraper_name}: {str(e)}'
                        print(f'Error with {scraper_name}: {e}')
                        errors.append(error_msg)
                        continue
        
        if resume_text:
            message = f'Found {total_saved} new jobs with AI match scores ({total_duplicates} duplicates skipped)'
        else:
            message = f'Found {total_saved} new jobs ({total_duplicates} duplicates skipped). Upload resume for AI match scores.'
        
        if errors:
            message += f' | Errors: {"; ".join(errors)}'
        
        return jsonify({
            'success': True,
            'message': message,
            'saved': total_saved,
            'duplicates': total_duplicates
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error scraping jobs: {str(e)}'
        }), 500


@app.route('/api/jobs/list', methods=['GET'])
def list_jobs():
    """Get list of jobs for dropdown"""
    jobs = Job.query.order_by(Job.scraped_date.desc()).limit(100).all()
    return jsonify([{
        'id': job.id,
        'title': job.title,
        'company': job.company
    } for job in jobs])


@app.route('/api/interview/schedule', methods=['POST'])
def schedule_interview():
    """Schedule an interview"""
    data = request.get_json()
    job_id = data.get('job_id')
    scheduled_date = data.get('scheduled_date')  # ISO format string
    interview_type = data.get('interview_type', 'phone')
    notes = data.get('notes', '')
    
    # Get or create application
    application = Application.query.filter_by(job_id=job_id).first()
    if not application:
        application = Application(job_id=job_id, status='interview')
        db.session.add(application)
        db.session.flush()
    elif application.status not in ['interview', 'offer']:
        application.status = 'interview'
    
    # Create interview
    try:
        # Parse the date - accept multiple formats
        if 'T' in scheduled_date:
            parsed_date = datetime.fromisoformat(scheduled_date.replace('Z', '+00:00'))
        else:
            # Handle simple format like "2026-03-15 14:00"
            parsed_date = datetime.strptime(scheduled_date, '%Y-%m-%d %H:%M')
    except:
        return jsonify({'success': False, 'message': 'Invalid date format. Use YYYY-MM-DD HH:MM'}), 400
    
    interview = Interview(
        application_id=application.id,
        scheduled_date=parsed_date,
        interview_type=interview_type,
        notes=notes
    )
    db.session.add(interview)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Interview scheduled'})


@app.route('/api/interview/<int:interview_id>/delete', methods=['DELETE'])
def delete_interview(interview_id):
    """Delete an interview"""
    interview = Interview.query.get_or_404(interview_id)
    
    db.session.delete(interview)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Interview deleted'})


@app.route('/api/cover-letter/generate', methods=['POST'])
def generate_cover_letter_api():
    """Generate cover letter for a job using AI"""
    try:
        data = request.get_json()
        job_id = data.get('job_id')
        
        job = Job.query.get_or_404(job_id)
        
        # Get resume
        resume = Resume.query.first()
        if not resume or not resume.filepath:
            return jsonify({'success': False, 'message': 'Please upload your resume first'}), 400
        
        # Parse resume
        from ai.resume_parser import parse_resume
        resume_text = parse_resume(resume.filepath)
        
        if not resume_text:
            return jsonify({'success': False, 'message': 'Could not read resume file'}), 400
        
        # Get user preferences for context
        prefs = SearchPreferences.query.first()
        user_prefs = None
        if prefs:
            user_prefs = {
                'search_description': prefs.search_description,
                'keywords': prefs.keywords
            }
        
        # Generate cover letter with AI
        from ai.cover_letter import generate_cover_letter
        cover_letter = generate_cover_letter(resume_text, job, user_prefs)
        
        # Check if generation failed
        if cover_letter.startswith('Error:'):
            return jsonify({'success': False, 'message': cover_letter}), 500
        
        # Save to application
        application = Application.query.filter_by(job_id=job_id).first()
        if not application:
            application = Application(job_id=job_id)
            db.session.add(application)
        
        application.cover_letter = cover_letter
        db.session.commit()
        
        return jsonify({'success': True, 'cover_letter': cover_letter})
    
    except Exception as e:
        print(f'Cover letter generation error: {e}')
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500


@app.cli.command()
def calculate_matches():
    """Calculate AI match scores for all jobs"""
    from ai.resume_parser import parse_resume
    from ai.job_matcher import calculate_match_score
    
    # Get resume
    resume = Resume.query.first()
    if not resume or not resume.filepath:
        print('❌ Error: No resume uploaded')
        return
    
    # Parse resume
    print('📄 Parsing resume...')
    resume_text = parse_resume(resume.filepath)
    
    if not resume_text:
        print('❌ Error: Could not read resume')
        return
    
    # Get all jobs without match scores (or with placeholder 75)
    jobs = Job.query.filter(
        (Job.match_score == None) | (Job.match_score == 75)
    ).all()
    
    print(f'🔍 Calculating match scores for {len(jobs)} jobs...')
    
    updated = 0
    for i, job in enumerate(jobs, 1):
        try:
            score, explanation = calculate_match_score(resume_text, job)
            job.match_score = score
            job.match_explanation = explanation
            updated += 1
            
            if i % 5 == 0:
                print(f'   Processed {i}/{len(jobs)}...')
                db.session.commit()  # Commit in batches
        except Exception as e:
            print(f'   ⚠️  Error scoring job {job.id}: {e}')
            continue
    
    db.session.commit()
    print(f'\n✅ Updated {updated} job match scores!')


@app.cli.command()
def init_db():
    """Initialize the database"""
    db.create_all()
    print('Database initialized!')


@app.cli.command()
def scrape_jobs():
    """Run job scrapers"""
    from scrapers.adzuna_api import AdzunaAPIScraper
    
    try:
        from scrapers.indeed_playwright import IndeedPlaywrightScraper as IndeedScraper
        print('✅ Indeed scraper available (Playwright)')
        scrapers = [('Indeed', IndeedScraper)]
    except ImportError:
        print('⚠️  Indeed scraper not available (Playwright not installed)')
        scrapers = []
    
    # Add Adzuna API scraper
    scrapers.append(('Adzuna', AdzunaAPIScraper))
    
    from ai.resume_parser import parse_resume
    from ai.job_matcher import calculate_match_score
    
    # Get search preferences
    prefs = SearchPreferences.query.first()
    
    if not prefs or not prefs.job_titles:
        print('⚠️  No search preferences found. Please add job titles and keywords first.')
        print('   Visit the Settings page in the web app to configure.')
        return
    
    # Get resume for AI matching
    resume = Resume.query.first()
    resume_text = None
    if resume and resume.filepath:
        print('📄 Resume found - will calculate AI match scores')
        resume_text = parse_resume(resume.filepath)
    else:
        print('⚠️  No resume uploaded - using placeholder match scores')
    
    # Parse job titles and locations
    job_titles = [t.strip() for t in prefs.job_titles.split(',') if t.strip()]
    locations = [l.strip() for l in (prefs.locations or 'Portland, OR').split(',') if l.strip()]
    
    total_saved = 0
    total_duplicates = 0
    
    # Loop through all scrapers
    for scraper_name, ScraperClass in scrapers:
        print(f'\n{"="*60}')
        print(f'🔍 Using {scraper_name} scraper')
        print(f'{"="*60}')
        
        for title in job_titles:
            for location in locations:
                try:
                    scraper = ScraperClass()
                    jobs = scraper.scrape(keywords=title, location=location, max_results=50)
                    
                    if not jobs:
                        continue
                    
                    # Save jobs to database
                    for job_data in jobs:
                        try:
                            # Check if job already exists
                            existing = Job.query.filter_by(
                                source=job_data['source'],
                                external_id=job_data['external_id']
                            ).first()
                            
                            if existing:
                                total_duplicates += 1
                                continue
                            
                            # Create new job
                            job = Job(
                                source=job_data['source'],
                                external_id=job_data['external_id'],
                                url=job_data['url'],
                                title=job_data['title'],
                                company=job_data['company'],
                                location=job_data['location'],
                                salary_min=job_data.get('salary_min'),
                                salary_max=job_data.get('salary_max'),
                                description=job_data['description'],
                                requirements=job_data.get('requirements'),
                                posted_date=job_data.get('posted_date'),
                                scraped_date=datetime.utcnow(),
                                match_score=75  # Temporary - will calculate below
                            )
                            
                            db.session.add(job)
                            db.session.flush()  # Get the job ID
                            
                            # Calculate real match score with AI if resume available
                            if resume_text:
                                try:
                                    match_score, explanation = calculate_match_score(resume_text, job)
                                    job.match_score = match_score
                                    job.match_explanation = explanation
                                    print(f'   ✓ {job.title[:40]}... → {match_score}%')
                                except Exception as e:
                                    print(f'   ⚠️  Error scoring {job.title[:30]}: {e}')
                                    job.match_score = 75  # Fallback to placeholder
                                    job.match_explanation = None
                            
                            total_saved += 1
                            
                        except Exception as e:
                            print(f'   ❌ Error saving job: {e}')
                            continue
                    
                    db.session.commit()
                    
                except Exception as e:
                    print(f'   ❌ Error with {scraper_name} scraper: {e}')
                    continue
    
    print(f'\n{"="*60}')
    print(f'✅ Scraping complete!')
    print(f'   💾 Saved: {total_saved} new jobs')
    print(f'   ⏭️  Skipped: {total_duplicates} duplicates')
    if resume_text:
        print(f'   🧠 All jobs scored with AI')
    print(f'\n   Visit http://localhost:5000 to view jobs!')
    print(f'{"="*60}')


if __name__ == '__main__':
    # Create tables on first run
    with app.app_context():
        db.create_all()
    
    app.run(debug=True, host='0.0.0.0', port=5000)
