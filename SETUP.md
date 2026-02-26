# Setup Guide - Job Search Platform

## Quick Start

### 1. Create Virtual Environment

```powershell
cd C:\job_search_platform

# Create virtual environment
python -m venv venv

# Activate it
.\venv\Scripts\activate
```

### 2. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 3. Configure Environment

```powershell
# Copy example env file
copy .env.example .env

# Edit .env with your settings
notepad .env
```

**Required settings:**
- `CLAUDE_API_KEY` - Get from https://console.anthropic.com/settings/keys
- Leave others blank for now (optional features)

### 4. Initialize Database

```powershell
python
>>> from app import db, app
>>> with app.app_context():
...     db.create_all()
>>> exit()
```

Or use the CLI command:
```powershell
flask init-db
```

### 5. Run the Application

```powershell
python app.py
```

Visit: **http://localhost:5000**

---

## First Time Setup

### Upload Your Resume

1. Click "Upload Resume" in the top nav (coming soon)
2. Or manually add to database for now

### Scrape Jobs

```powershell
# Run scrapers manually
python
>>> from app import app
>>> with app.app_context():
...     from scrapers.indeed import IndeedScraper
...     scraper = IndeedScraper()
...     jobs = scraper.scrape('python developer', 'Portland, OR')
...     scraper.save_jobs()
>>> exit()
```

Or use the CLI:
```powershell
flask scrape-jobs
```

### Test the UI

1. **Jobs page** - View scraped jobs
2. **Job detail** - Click any job to see details
3. **Applications** - Drag jobs between status columns
4. **Analytics** - View your progress

---

## Optional Features

### Gmail Integration (Email Monitoring)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable Gmail API
4. Create OAuth 2.0 credentials
5. Add to `.env`:
   ```
   GMAIL_CLIENT_ID=your-client-id
   GMAIL_CLIENT_SECRET=your-secret
   GMAIL_REFRESH_TOKEN=your-token
   ```

### Telegram Notifications

1. Talk to [@BotFather](https://t.me/BotFather) on Telegram
2. Create a new bot with `/newbot`
3. Get your bot token
4. Send a message to your bot
5. Visit: `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates`
6. Find your `chat_id`
7. Add to `.env`:
   ```
   TELEGRAM_BOT_TOKEN=123456:ABC-DEF...
   TELEGRAM_CHAT_ID=123456789
   ```

### OpenClaw Integration

Add a cron job for daily scraping:

```javascript
// In OpenClaw
{
  "name": "Daily Job Scrape",
  "schedule": { "kind": "cron", "expr": "0 8 * * *", "tz": "America/Los_Angeles" },
  "payload": {
    "kind": "systemEvent",
    "text": "Run job scraper: cd C:\\job_search_platform && venv\\Scripts\\activate && flask scrape-jobs"
  },
  "sessionTarget": "main",
  "enabled": true
}
```

---

## Development

### Project Structure

```
job_search_platform/
├── app.py                 # Flask app + routes
├── models.py              # Database models
├── config.py              # Configuration
├── requirements.txt       # Dependencies
│
├── scrapers/              # Job board scrapers
│   ├── base.py
│   ├── indeed.py
│   ├── linkedin.py
│   └── ziprecruiter.py
│
├── templates/             # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── job_detail.html
│   ├── applications.html
│   └── analytics.html
│
└── static/                # CSS, JS, uploads
    └── uploads/
```

### Run in Development Mode

```powershell
$env:FLASK_ENV="development"
python app.py
```

The app will auto-reload on code changes.

### Database Commands

```powershell
# Initialize database
flask init-db

# Run scrapers
flask scrape-jobs

# Python shell with app context
python
>>> from app import *
>>> # Do stuff...
```

---

## Next Steps

### Phase 1 (Complete ✅)
- ✅ Basic Flask app
- ✅ Job scrapers (Indeed, LinkedIn, ZipRecruiter)
- ✅ Job listings UI
- ✅ Application tracker (Kanban)
- ✅ Analytics dashboard

### Phase 2 (TODO)
- [ ] Resume upload & parsing
- [ ] AI job matching (Claude)
- [ ] Cover letter generation
- [ ] Company research chat agent

### Phase 3 (TODO)
- [ ] Gmail monitoring
- [ ] Telegram notifications
- [ ] Scheduled scraping (Celery)

### Phase 4 (TODO)
- [ ] Advanced analytics
- [ ] Export data (CSV, PDF)
- [ ] Goal tracking

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'flask'"

Make sure virtual environment is activated:
```powershell
.\venv\Scripts\activate
```

### "No jobs found" after scraping

Job boards may have changed their HTML. Check scraper code and update selectors if needed.

### Scrapers not working

- Indeed, LinkedIn, ZipRecruiter may rate-limit or require authentication
- Consider using official APIs for production
- Add delays between requests
- Use proxies or rotating user agents

### Database errors

Delete `jobs.db` and re-run `flask init-db` to start fresh.

---

## Production Deployment

### Option 1: Railway

1. Create account at https://railway.app
2. Connect GitHub repo
3. Add environment variables
4. Deploy!

### Option 2: Render

1. Create account at https://render.com
2. New Web Service → Connect repo
3. Build command: `pip install -r requirements.txt`
4. Start command: `python app.py`
5. Add environment variables

### Option 3: Fly.io

```powershell
# Install flyctl
fly launch
fly deploy
```

---

## Support

- Check README.md for overview
- See WIREFLOW.md for UI designs
- See PROJECT_PLAN.md for roadmap

Built with ❤️ and OpenClaw 🤖
