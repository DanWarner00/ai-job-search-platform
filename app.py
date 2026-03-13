"""
Job Search Platform - Main Application
"""
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from config import config
from models import db, User, Job, Application, Interview, Resume, SearchPreferences
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import os

app = Flask(__name__)
env = os.getenv('FLASK_ENV', 'development')
app.config.from_object(config[env])
db.init_app(app)
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# ── AUTH EXTENSIONS ───────────────────────────────────────────────────────────

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

csrf = CSRFProtect(app)
limiter = Limiter(get_remote_address, app=app, default_limits=[])
mail = Mail(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ── HELPERS ──────────────────────────────────────────────────────────────────

def _get_active_prefs(user_id=None):
    """Return the active SearchPreferences profile for a user.
    Uses current_user if in request context and no user_id given."""
    if user_id is None:
        try:
            if current_user.is_authenticated:
                user_id = current_user.id
        except RuntimeError:
            pass  # Outside request context (CLI)
    if user_id is None:
        return None
    return (SearchPreferences.query.filter_by(user_id=user_id, is_active=True).first()
            or SearchPreferences.query.filter_by(user_id=user_id).first())


def _get_profile_resume(prefs=None):
    """Return the Resume record for the given profile (or active profile)."""
    if prefs is None:
        prefs = _get_active_prefs()
    if prefs:
        resume = Resume.query.filter_by(profile_id=prefs.id).first()
        if resume:
            return resume
    return None


def _get_resume_text():
    """Parse and return the active profile's resume text, or None."""
    resume = _get_profile_resume()
    if not resume or not resume.filepath:
        return None
    if resume.content:
        return resume.content
    from ai.resume_parser import parse_resume
    return parse_resume(resume.filepath)


def _save_jobs(jobs_data, resume_text, prefs=None, user_id=None):
    """
    Persist a list of scraped job dicts, skipping duplicates and calculating
    AI match scores when a resume is available.
    Returns (saved_count, duplicate_count).
    """
    from ai.job_matcher import calculate_match_score
    saved = dupes = 0
    for job_data in jobs_data:
        try:
            if Job.query.filter_by(
                source=job_data['source'],
                external_id=job_data['external_id'],
                user_id=user_id
            ).first():
                dupes += 1
                continue

            job = Job(
                user_id=user_id,
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
                match_score=75,
            )
            db.session.add(job)
            db.session.flush()

            if resume_text:
                try:
                    score, explanation = calculate_match_score(resume_text, job, prefs)
                    job.match_score = score
                    job.match_explanation = explanation
                except Exception as e:
                    print(f'Match score error: {e}')

            saved += 1
        except Exception as e:
            print(f'Error saving job: {e}')

    db.session.commit()
    return saved, dupes


def _scrape_and_save(scraper_classes, source_label, verbose=False):
    """
    Orchestrate a web-triggered scrape: validate prefs, run scrapers, persist
    results. Returns (saved, dupes, message) — saved=None signals a 400 error.
    verbose=True passes through to scrapers that support it (Indeed) for full descriptions.
    """
    prefs = _get_active_prefs()
    if not prefs or not prefs.job_titles:
        return None, None, 'Please set search preferences first (job titles required)'

    resume_text = _get_resume_text()
    job_titles  = [t.strip() for t in prefs.job_titles.split(',') if t.strip()]
    locations   = prefs.get_locations_list() or ['Portland, OR']
    user_id     = current_user.id

    import inspect
    total_saved = total_dupes = 0
    for ScraperClass in scraper_classes:
        for title in job_titles[:2]:
            for location in locations:
                scraper = ScraperClass()
                # Only pass verbose if the scraper's scrape() method accepts it
                sig = inspect.signature(scraper.scrape)
                if 'verbose' in sig.parameters:
                    jobs = scraper.scrape(keywords=title, location=location, max_results=25, verbose=verbose)
                else:
                    jobs = scraper.scrape(keywords=title, location=location, max_results=25)
                if jobs:
                    s, d = _save_jobs(jobs, resume_text, prefs, user_id=user_id)
                    total_saved += s
                    total_dupes += d

    if resume_text:
        msg = f'{source_label}: {total_saved} new jobs with AI scores ({total_dupes} duplicates skipped)'
    else:
        msg = f'{source_label}: {total_saved} new jobs ({total_dupes} duplicates skipped). Upload resume for AI scores.'

    return total_saved, total_dupes, msg


# ── CONTEXT PROCESSOR ────────────────────────────────────────────────────────

@app.context_processor
def inject_global_context():
    if not current_user.is_authenticated:
        return {}
    prefs  = _get_active_prefs()
    resume = _get_profile_resume(prefs)
    return {
        'has_resume':      resume is not None,
        'has_preferences': prefs is not None and bool(prefs.job_titles),
        'resume':          resume,
        'preferences':     prefs,
        'jobs_count':      Job.query.filter_by(user_id=current_user.id).count(),
    }


# ── AUTH ROUTES ───────────────────────────────────────────────────────────────

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email    = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm  = request.form.get('confirm_password', '')

        if not username or not email or not password:
            flash('All fields are required.', 'error')
            return render_template('register.html')
        if len(password) < 8:
            flash('Password must be at least 8 characters.', 'error')
            return render_template('register.html')
        if password != confirm:
            flash('Passwords do not match.', 'error')
            return render_template('register.html')
        if User.query.filter_by(username=username).first():
            flash('Username already taken.', 'error')
            return render_template('register.html')
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'error')
            return render_template('register.html')

        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        login_user(user)
        flash(f'Welcome, {username}! Set up your search profile to get started.', 'success')
        return redirect(url_for('settings'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
@limiter.limit("20 per minute")
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user, remember=request.form.get('remember_me') == 'on')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        flash('Invalid username or password.', 'error')
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        user  = User.query.filter_by(email=email).first()
        # Always show the same message to prevent email enumeration
        if user:
            s     = URLSafeTimedSerializer(app.config['SECRET_KEY'])
            token = s.dumps(user.email, salt='password-reset')
            reset_url = url_for('reset_password', token=token, _external=True)
            msg = Message('Reset your password', recipients=[user.email])
            msg.body = (
                f'Hi {user.username},\n\n'
                f'Click the link below to reset your password. This link expires in 1 hour.\n\n'
                f'{reset_url}\n\n'
                f'If you did not request a password reset, ignore this email.'
            )
            try:
                mail.send(msg)
            except Exception as e:
                print(f'Mail error: {e}')
        flash('If that email is registered, a reset link has been sent.', 'info')
        return redirect(url_for('login'))
    return render_template('forgot_password.html')


@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    s = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    try:
        email = s.loads(token, salt='password-reset', max_age=3600)
    except (SignatureExpired, BadSignature):
        flash('The reset link is invalid or has expired.', 'error')
        return redirect(url_for('forgot_password'))

    user = User.query.filter_by(email=email).first_or_404()

    if request.method == 'POST':
        password = request.form.get('password', '')
        confirm  = request.form.get('confirm_password', '')
        if len(password) < 8:
            flash('Password must be at least 8 characters.', 'error')
            return render_template('reset_password.html', token=token)
        if password != confirm:
            flash('Passwords do not match.', 'error')
            return render_template('reset_password.html', token=token)
        user.set_password(password)
        db.session.commit()
        flash('Password reset! You can now log in.', 'success')
        return redirect(url_for('login'))

    return render_template('reset_password.html', token=token)


# ── PAGE ROUTES ──────────────────────────────────────────────────────────────

@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/')
@login_required
def index():
    min_score    = request.args.get('min_score', 0,     type=int)
    max_score    = request.args.get('max_score', 100,   type=int)
    location     = request.args.get('location', '')
    source       = request.args.get('source',   '')
    starred_only = request.args.get('starred',  '')
    page         = request.args.get('page',     1,      type=int)
    sort_by      = request.args.get('sort_by',  'match')

    query = Job.query.filter(
        Job.user_id == current_user.id,
        Job.match_score >= min_score,
        Job.match_score <= max_score,
    )
    if location:
        query = query.filter(Job.location.like(f'%{location}%'))
    if source:
        query = query.filter(Job.source == source)
    if starred_only:
        query = query.filter(Job.starred == True)

    if sort_by == 'posted':
        query = query.order_by(Job.starred.desc(), Job.posted_date.desc().nullslast())
    elif sort_by == 'scraped':
        query = query.order_by(Job.starred.desc(), Job.scraped_date.desc())
    else:
        query = query.order_by(Job.starred.desc(), Job.match_score.desc(), Job.posted_date.desc().nullslast())

    jobs = query.paginate(page=page, per_page=app.config['JOBS_PER_PAGE'], error_out=False)

    stats = {
        'total_jobs': Job.query.filter_by(user_id=current_user.id).count(),
        'applied':    Application.query.join(Job).filter(
                          Job.user_id == current_user.id,
                          Application.status == 'applied',
                      ).count(),
        'interviews': Application.query.join(Job).filter(
                          Job.user_id == current_user.id,
                          Application.status == 'interview',
                      ).count(),
        'high_match': Job.query.filter(
                          Job.user_id == current_user.id,
                          Job.match_score >= 80,
                      ).count(),
    }

    source_counts = (db.session.query(Job.source, db.func.count(Job.id))
                     .filter(Job.user_id == current_user.id)
                     .group_by(Job.source).all())
    source_stats  = {src: cnt for src, cnt in source_counts}

    return render_template('index.html', jobs=jobs, stats=stats,
                           min_score=min_score, max_score=max_score,
                           location=location, source=source, sort_by=sort_by,
                           starred_only=starred_only, source_stats=source_stats)


@app.route('/job/<int:job_id>')
@login_required
def job_detail(job_id):
    job         = Job.query.filter_by(id=job_id, user_id=current_user.id).first_or_404()
    application = Application.query.filter_by(job_id=job_id).first()
    return render_template('job_detail.html', job=job, application=application)


@app.route('/applications')
@login_required
def applications():
    three_weeks_ago = datetime.utcnow() - timedelta(weeks=3)

    not_applied = (Job.query
                   .filter_by(user_id=current_user.id)
                   .outerjoin(Application)
                   .filter((Application.id == None) | (Application.status == 'not_applied'))
                   .order_by(Job.match_score.desc())
                   .limit(200).all())

    applied = (Application.query.join(Job)
               .filter(Job.user_id == current_user.id,
                       Application.status == 'applied',
                       Application.applied_date > three_weeks_ago)
               .order_by(Application.applied_date.desc()).all())

    inactive = (Application.query.join(Job)
                .filter(Job.user_id == current_user.id,
                        Application.status == 'applied',
                        Application.applied_date <= three_weeks_ago)
                .order_by(Application.applied_date.desc()).all())

    interviews = (Application.query.join(Job)
                  .filter(Job.user_id == current_user.id,
                          Application.status == 'interview')
                  .order_by(Application.applied_date.desc()).all())

    rejected = (Application.query.join(Job)
                .filter(Job.user_id == current_user.id,
                        Application.status == 'rejected')
                .order_by(Application.updated_at.desc()).all())

    not_interested = (Application.query.join(Job)
                      .filter(Job.user_id == current_user.id,
                              Application.status == 'not_interested')
                      .order_by(Application.updated_at.desc()).all())

    return render_template('applications.html',
                           not_applied=not_applied, applied=applied,
                           interviews=interviews, rejected=rejected,
                           inactive=inactive, not_interested=not_interested)


@app.route('/calendar')
@login_required
def calendar():
    from calendar import monthcalendar, month_name, setfirstweekday
    setfirstweekday(6)  # 6 = Sunday, matching the Sun-Sat header order in the template
    from datetime import date

    now   = datetime.now()
    year  = request.args.get('year',  now.year,  type=int)
    month = request.args.get('month', now.month, type=int)

    start_date = date(year, month, 1)
    end_date   = date(year + 1, 1, 1) if month == 12 else date(year, month + 1, 1)

    interviews = (Interview.query
                  .join(Application)
                  .join(Job, Application.job_id == Job.id)
                  .filter(Job.user_id == current_user.id,
                          Interview.scheduled_date >= start_date,
                          Interview.scheduled_date < end_date)
                  .all())

    interviews_by_date = {}
    for iv in interviews:
        key = iv.scheduled_date.date() if iv.scheduled_date else None
        if key:
            interviews_by_date.setdefault(key, []).append(iv)

    prev_month = 12     if month == 1  else month - 1
    prev_year  = year-1 if month == 1  else year
    next_month = 1      if month == 12 else month + 1
    next_year  = year+1 if month == 12 else year

    upcoming_interviews = (Interview.query
                           .join(Application)
                           .join(Job, Application.job_id == Job.id)
                           .filter(Job.user_id == current_user.id,
                                   Interview.scheduled_date >= now)
                           .order_by(Interview.scheduled_date)
                           .limit(10).all())

    return render_template('calendar.html',
                           calendar=monthcalendar(year, month),
                           month=month, month_name=month_name[month], year=year,
                           interviews_by_date=interviews_by_date,
                           today=now.date(),
                           prev_month=prev_month, prev_year=prev_year,
                           next_month=next_month, next_year=next_year,
                           upcoming_interviews=upcoming_interviews)


@app.route('/analytics')
@login_required
def analytics():
    stats = {
        'viewed':     Job.query.filter_by(user_id=current_user.id).count(),
        'applied':    Application.query.join(Job).filter(
                          Job.user_id == current_user.id,
                          Application.status.in_(['applied', 'interview', 'rejected', 'offer'])
                      ).count(),
        'interviews': Application.query.join(Job).filter(
                          Job.user_id == current_user.id,
                          Application.status == 'interview',
                      ).count(),
        'offers':     Application.query.join(Job).filter(
                          Job.user_id == current_user.id,
                          Application.status == 'offer',
                      ).count(),
    }
    return render_template('analytics.html', stats=stats)


@app.route('/settings')
@login_required
def settings():
    all_profiles = SearchPreferences.query.filter_by(user_id=current_user.id).order_by(SearchPreferences.id).all()
    active_prefs = _get_active_prefs()
    resume       = _get_profile_resume(active_prefs)
    return render_template('settings.html',
                           resume=resume,
                           prefs=active_prefs,
                           all_profiles=all_profiles)


# ── API ROUTES ───────────────────────────────────────────────────────────────

@app.route('/upload-resume', methods=['POST'])
@login_required
@csrf.exempt
def upload_resume():
    if 'resume' not in request.files or request.files['resume'].filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('settings'))

    file = request.files['resume']
    ext  = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
    if ext not in {'pdf', 'docx'}:
        flash('Invalid file type. Please upload PDF or DOCX', 'error')
        return redirect(url_for('settings'))

    original_filename = file.filename
    timestamp         = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    stored_filename   = f'resume_{timestamp}.{ext}'

    upload_folder = app.config['UPLOAD_FOLDER']
    os.makedirs(upload_folder, exist_ok=True)
    filepath = os.path.join(upload_folder, stored_filename)

    try:
        file.save(filepath)
    except Exception as e:
        flash(f'Failed to save file: {e}', 'error')
        return redirect(url_for('settings'))

    parsed_text = None
    try:
        from ai.resume_parser import parse_resume
        parsed_text = parse_resume(filepath)
    except Exception as e:
        app.logger.warning(f'Resume parsing failed: {e}')

    active_prefs = _get_active_prefs()
    profile_id   = active_prefs.id if active_prefs else None

    resume = Resume.query.filter_by(profile_id=profile_id).first() or Resume(profile_id=profile_id)
    resume.filename    = original_filename
    resume.filepath    = filepath
    resume.content     = parsed_text
    resume.uploaded_at = datetime.utcnow()
    db.session.add(resume)
    db.session.commit()

    if parsed_text:
        flash('Resume uploaded and parsed successfully!', 'success')
    else:
        flash('Resume uploaded, but text extraction failed — AI scoring may not work. Try a plain-text PDF or DOCX.', 'warning')
    return redirect(url_for('settings'))


@app.route('/api/resume/save-text', methods=['POST'])
@login_required
@csrf.exempt
def save_resume_text():
    text = (request.get_json(silent=True) or {}).get('text', '').strip()
    if not text:
        return jsonify({'success': False, 'message': 'No text provided'}), 400

    active_prefs = _get_active_prefs()
    profile_id   = active_prefs.id if active_prefs else None

    resume = Resume.query.filter_by(profile_id=profile_id).first() or Resume(profile_id=profile_id)
    resume.filename    = 'pasted_resume.txt'
    resume.filepath    = None
    resume.content     = text
    resume.uploaded_at = datetime.utcnow()
    db.session.add(resume)
    db.session.commit()
    return jsonify({'success': True})


@app.route('/api/preferences/update', methods=['POST'])
@login_required
@csrf.exempt
def update_preferences():
    data     = request.get_json()
    prefs_id = data.get('id')
    if prefs_id:
        prefs = SearchPreferences.query.filter_by(id=prefs_id, user_id=current_user.id).first()
        if not prefs:
            return jsonify({'success': False, 'message': 'Profile not found'}), 404
    else:
        prefs = _get_active_prefs() or SearchPreferences(user_id=current_user.id)

    prefs.name               = data.get('name', prefs.name or 'Default')
    prefs.job_titles         = data.get('job_titles', '')
    prefs.keywords           = data.get('keywords', '')
    prefs.search_description = data.get('search_description', '')
    prefs.work_experience    = data.get('work_experience', '')
    prefs.locations          = data.get('locations', '')
    prefs.min_salary         = data.get('min_salary')
    prefs.max_salary         = data.get('max_salary')
    prefs.remote_only        = data.get('remote_only', False)
    db.session.add(prefs)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Preferences updated successfully', 'id': prefs.id})


@app.route('/api/preferences/create', methods=['POST'])
@login_required
@csrf.exempt
def create_preferences():
    data  = request.get_json()
    prefs = SearchPreferences(
        user_id=current_user.id,
        name=data.get('name', 'New Profile'),
        is_active=False,
        job_titles='',
        locations='',
    )
    db.session.add(prefs)
    db.session.commit()
    return jsonify({'success': True, 'id': prefs.id, 'name': prefs.name})


@app.route('/api/preferences/activate/<int:prefs_id>', methods=['POST'])
@login_required
@csrf.exempt
def activate_preferences(prefs_id):
    target = SearchPreferences.query.filter_by(id=prefs_id, user_id=current_user.id).first_or_404()
    SearchPreferences.query.filter_by(user_id=current_user.id).update({'is_active': False})
    target.is_active = True
    db.session.commit()
    return jsonify({'success': True, 'message': f'"{target.name}" is now the active profile'})


@app.route('/api/jobs/clear-all', methods=['DELETE'])
@login_required
@csrf.exempt
def clear_all_jobs():
    count = Job.query.filter_by(user_id=current_user.id).count()
    Job.query.filter_by(user_id=current_user.id).delete()
    db.session.commit()
    return jsonify({'success': True, 'message': f'Deleted {count} jobs'})


@app.route('/api/job/<int:job_id>/star', methods=['POST'])
@login_required
@csrf.exempt
def star_job(job_id):
    job = Job.query.filter_by(id=job_id, user_id=current_user.id).first_or_404()
    job.starred = not job.starred
    db.session.commit()
    return jsonify({'success': True, 'starred': job.starred})


@app.route('/api/job/<int:job_id>/delete', methods=['DELETE'])
@login_required
@csrf.exempt
def delete_job(job_id):
    job = Job.query.filter_by(id=job_id, user_id=current_user.id).first_or_404()
    db.session.delete(job)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Job deleted'})


@app.route('/api/preferences/delete/<int:prefs_id>', methods=['DELETE'])
@login_required
@csrf.exempt
def delete_preferences(prefs_id):
    if SearchPreferences.query.filter_by(user_id=current_user.id).count() <= 1:
        return jsonify({'success': False, 'message': 'Cannot delete the only profile'}), 400
    prefs      = SearchPreferences.query.filter_by(id=prefs_id, user_id=current_user.id).first_or_404()
    was_active = prefs.is_active
    db.session.delete(prefs)
    db.session.flush()
    if was_active:
        fallback = SearchPreferences.query.filter_by(user_id=current_user.id).first()
        if fallback:
            fallback.is_active = True
    db.session.commit()
    return jsonify({'success': True, 'message': 'Profile deleted'})


@app.route('/api/application/update', methods=['POST'])
@login_required
@csrf.exempt
def update_application():
    data   = request.get_json()
    job_id = data.get('job_id')
    if not Job.query.filter_by(id=job_id, user_id=current_user.id).first():
        return jsonify({'success': False, 'message': 'Job not found'}), 404

    application = Application.query.filter_by(job_id=job_id).first() \
                  or Application(job_id=job_id)
    application.status           = data.get('status')
    application.rejection_reason = data.get('rejection_reason', '')
    application.notes            = data.get('notes', '')
    if application.status == 'applied':
        application.applied_date = datetime.utcnow()
    db.session.add(application)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Application updated'})


@app.route('/api/scrape/indeed', methods=['POST'])
@login_required
@csrf.exempt
def scrape_indeed():
    try:
        from scrapers.indeed_playwright import IndeedPlaywrightScraper
    except ImportError:
        return jsonify({'success': False, 'message': 'Indeed scraper not available (Playwright not installed)'}), 400
    verbose = (request.get_json(silent=True) or {}).get('verbose', False)
    try:
        saved, dupes, msg = _scrape_and_save([IndeedPlaywrightScraper], 'Indeed', verbose=verbose)
        if saved is None:
            return jsonify({'success': False, 'message': msg}), 400
        return jsonify({'success': True, 'message': msg, 'saved': saved, 'duplicates': dupes})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Indeed error: {str(e)}'}), 500


@app.route('/api/scrape/adzuna', methods=['POST'])
@login_required
@csrf.exempt
def scrape_adzuna():
    from scrapers.adzuna_api import AdzunaAPIScraper
    verbose = (request.get_json(silent=True) or {}).get('verbose', False)
    try:
        saved, dupes, msg = _scrape_and_save([AdzunaAPIScraper], 'Adzuna', verbose=verbose)
        if saved is None:
            return jsonify({'success': False, 'message': msg}), 400
        return jsonify({'success': True, 'message': msg, 'saved': saved, 'duplicates': dupes})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Adzuna error: {str(e)}'}), 500


@app.route('/api/scrape/run', methods=['POST'])
@login_required
@csrf.exempt
def run_scraper():
    from scrapers.adzuna_api import AdzunaAPIScraper
    scraper_classes = []
    try:
        from scrapers.indeed_playwright import IndeedPlaywrightScraper
        scraper_classes.append(IndeedPlaywrightScraper)
    except ImportError:
        pass
    scraper_classes.append(AdzunaAPIScraper)
    try:
        saved, dupes, msg = _scrape_and_save(scraper_classes, 'All sources')
        if saved is None:
            return jsonify({'success': False, 'message': msg}), 400
        return jsonify({'success': True, 'message': msg, 'saved': saved, 'duplicates': dupes})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500


@app.route('/api/jobs/list', methods=['GET'])
@login_required
@csrf.exempt
def list_jobs():
    jobs = Job.query.filter_by(user_id=current_user.id).order_by(Job.scraped_date.desc()).limit(100).all()
    return jsonify([{'id': j.id, 'title': j.title, 'company': j.company} for j in jobs])


@app.route('/api/interview/schedule', methods=['POST'])
@login_required
@csrf.exempt
def schedule_interview():
    data           = request.get_json()
    job_id         = data.get('job_id')
    scheduled_date = data.get('scheduled_date')
    interview_type = data.get('interview_type', 'phone')
    notes          = data.get('notes', '')

    if not Job.query.filter_by(id=job_id, user_id=current_user.id).first():
        return jsonify({'success': False, 'message': 'Job not found'}), 404

    application = Application.query.filter_by(job_id=job_id).first()
    if not application:
        application = Application(job_id=job_id, status='interview')
        db.session.add(application)
        db.session.flush()
    elif application.status not in ['interview', 'offer']:
        application.status = 'interview'

    try:
        if 'T' in scheduled_date:
            parsed_date = datetime.fromisoformat(scheduled_date.replace('Z', '+00:00'))
        else:
            parsed_date = datetime.strptime(scheduled_date, '%Y-%m-%d %H:%M')
    except Exception:
        return jsonify({'success': False, 'message': 'Invalid date format. Use YYYY-MM-DD HH:MM'}), 400

    db.session.add(Interview(
        application_id=application.id,
        scheduled_date=parsed_date,
        interview_type=interview_type,
        notes=notes,
    ))
    db.session.commit()
    return jsonify({'success': True, 'message': 'Interview scheduled'})


@app.route('/api/interview/<int:interview_id>/delete', methods=['DELETE'])
@login_required
@csrf.exempt
def delete_interview(interview_id):
    interview = (Interview.query
                 .join(Application)
                 .join(Job, Application.job_id == Job.id)
                 .filter(Interview.id == interview_id, Job.user_id == current_user.id)
                 .first_or_404())
    db.session.delete(interview)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Interview deleted'})


@app.route('/api/cover-letter/generate', methods=['POST'])
@login_required
@csrf.exempt
def generate_cover_letter_api():
    try:
        job    = Job.query.filter_by(id=request.get_json().get('job_id'), user_id=current_user.id).first_or_404()
        resume = _get_profile_resume()
        if not resume or not resume.filepath:
            return jsonify({'success': False, 'message': 'Please upload your resume first'}), 400

        resume_text = _get_resume_text()
        if not resume_text:
            return jsonify({'success': False, 'message': 'Could not read resume file'}), 400

        prefs      = _get_active_prefs()
        user_prefs = {
            'search_description': prefs.search_description,
            'work_experience': prefs.work_experience,
            'keywords': prefs.keywords,
        } if prefs else None

        from ai.cover_letter import generate_cover_letter
        cover_letter = generate_cover_letter(resume_text, job, user_prefs)

        if cover_letter.startswith('Error:'):
            return jsonify({'success': False, 'message': cover_letter}), 500

        application = Application.query.filter_by(job_id=job.id).first() or Application(job_id=job.id)
        application.cover_letter = cover_letter
        db.session.add(application)
        db.session.commit()

        return jsonify({'success': True, 'cover_letter': cover_letter})
    except Exception as e:
        import traceback; traceback.print_exc()
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500


@app.route('/api/job/<int:job_id>/match-analysis', methods=['POST'])
@login_required
@csrf.exempt
def generate_match_analysis_api(job_id):
    try:
        job = Job.query.filter_by(id=job_id, user_id=current_user.id).first_or_404()
        resume_text = _get_resume_text()
        if not resume_text:
            return jsonify({'success': False, 'message': 'Please upload your resume first'}), 400

        prefs = _get_active_prefs()
        from ai.job_matcher import generate_match_analysis
        analysis = generate_match_analysis(resume_text, job, prefs)

        return jsonify({'success': True, 'analysis': analysis})
    except Exception as e:
        import traceback; traceback.print_exc()
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500


# ── CLI COMMANDS ─────────────────────────────────────────────────────────────

@app.cli.command()
def calculate_matches():
    """Calculate AI match scores for all unscored jobs (all users)."""
    from ai.job_matcher import calculate_match_score
    users = User.query.all()
    for user in users:
        prefs = _get_active_prefs(user_id=user.id)
        if not prefs:
            print(f'[{user.username}] No preferences, skipping')
            continue
        resume = _get_profile_resume(prefs)
        if not resume or not resume.content:
            print(f'[{user.username}] No resume, skipping')
            continue
        jobs = Job.query.filter(
            Job.user_id == user.id,
            (Job.match_score == None) | (Job.match_score == 75),
        ).all()
        print(f'[{user.username}] Scoring {len(jobs)} jobs...')
        updated = 0
        for i, job in enumerate(jobs, 1):
            try:
                job.match_score, job.match_explanation = calculate_match_score(resume.content, job, prefs)
                updated += 1
                if i % 5 == 0:
                    print(f'  {i}/{len(jobs)}...')
                    db.session.commit()
            except Exception as e:
                print(f'  Error scoring job {job.id}: {e}')
        db.session.commit()
        print(f'[{user.username}] Updated {updated} scores.')


@app.cli.command()
def init_db():
    """Initialize the database."""
    db.create_all()
    print('Database initialized.')


@app.cli.command()
def scrape_jobs():
    """Run job scrapers from the command line (all users with active prefs)."""
    from scrapers.adzuna_api import AdzunaAPIScraper
    scraper_classes = []
    try:
        from scrapers.indeed_playwright import IndeedPlaywrightScraper
        scraper_classes.append(('Indeed', IndeedPlaywrightScraper))
        print('Indeed scraper available')
    except ImportError:
        print('Indeed scraper not available (Playwright not installed)')
    scraper_classes.append(('Adzuna', AdzunaAPIScraper))

    users = User.query.all()
    for user in users:
        prefs = _get_active_prefs(user_id=user.id)
        if not prefs or not prefs.job_titles:
            print(f'[{user.username}] No search preferences, skipping')
            continue

        resume = _get_profile_resume(prefs)
        resume_text = resume.content if resume else None
        print(f'[{user.username}] Resume {"found" if resume_text else "not found"}')

        job_titles = [t.strip() for t in prefs.job_titles.split(',') if t.strip()]
        locations  = prefs.get_locations_list() or ['Portland, OR']

        total_saved = total_dupes = 0
        for name, ScraperClass in scraper_classes:
            print(f'  --- {name} ---')
            for title in job_titles:
                for location in locations:
                    try:
                        jobs = ScraperClass().scrape(keywords=title, location=location, max_results=50)
                        if jobs:
                            s, d = _save_jobs(jobs, resume_text, prefs, user_id=user.id)
                            total_saved += s
                            total_dupes += d
                            print(f'    {title} / {location}: {s} saved, {d} dupes')
                    except Exception as e:
                        print(f'    Error: {e}')

        print(f'[{user.username}] Done. {total_saved} saved, {total_dupes} duplicates skipped.')


# ── STARTUP ──────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)
