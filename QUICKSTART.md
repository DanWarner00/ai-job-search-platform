# 🚀 Quick Start - Get Running in 2 Minutes

## Method 1: One-Click Start (Windows)

**Just double-click `run.bat`** 

It will:
1. Create virtual environment
2. Install dependencies
3. Create .env file
4. Initialize database
5. Start the app

Then visit: **http://localhost:5000**

---

## Method 2: Manual Start

```powershell
# 1. Create & activate virtual environment
python -m venv venv
.\venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up environment
copy .env.example .env
# Edit .env - add your CLAUDE_API_KEY

# 4. Initialize database
python
>>> from app import db, app
>>> with app.app_context():
...     db.create_all()
>>> exit()

# 5. Run the app
python app.py
```

---

## First Steps After Running

### 1. **Browse Jobs** (http://localhost:5000)
- Empty initially - need to scrape jobs first

### 2. **Scrape Jobs**

Open a new terminal:
```powershell
cd C:\job_search_platform
.\venv\Scripts\activate

python
>>> from app import app
>>> with app.app_context():
...     from scrapers.indeed import IndeedScraper
...     scraper = IndeedScraper()
...     jobs = scraper.scrape('python developer', 'Portland, OR', max_results=20)
...     saved = scraper.save_jobs()
...     print(f'Saved {saved} jobs!')
>>> exit()
```

Refresh the web page - you'll see jobs!

### 3. **Explore Features**
- Click any job → View details
- Click "Mark Applied" → Track status
- Visit **Applications** → Drag jobs between columns
- Visit **Analytics** → View your progress

---

## What's Working Right Now

✅ **Job Scraping** - Indeed, LinkedIn, ZipRecruiter  
✅ **Job Listings** - Browse, filter, search  
✅ **Application Tracking** - Kanban board with drag-and-drop  
✅ **Analytics** - Funnels, charts, insights  
✅ **Job Details** - Full job view with actions  

## What Needs API Keys (Optional)

These features need configuration but app works without them:

⏳ **AI Job Matching** - Needs `CLAUDE_API_KEY`  
⏳ **Cover Letter Generation** - Needs `CLAUDE_API_KEY`  
⏳ **Company Research Chat** - Needs `CLAUDE_API_KEY`  
⏳ **Gmail Monitoring** - Needs Gmail API credentials  
⏳ **Telegram Notifications** - Needs Telegram bot token  

---

## Next Steps

1. **Test the UI** - Add jobs, track applications, view analytics
2. **Upload Resume** - (Coming soon - UI in progress)
3. **Add API Keys** - Edit `.env` to enable AI features
4. **Customize** - Edit scrapers, add your preferred job boards
5. **Deploy** - Use Railway, Render, or Fly.io for 24/7 access

---

## Troubleshooting

**Port 5000 already in use?**
```powershell
# Edit app.py, change last line to:
app.run(debug=True, host='0.0.0.0', port=3000)
```

**No jobs showing after scraping?**
- Check terminal output for errors
- Job boards may have changed HTML
- Try different keywords/location

**Database errors?**
```powershell
# Reset database
del jobs.db
python -c "from app import db, app; app.app_context().push(); db.create_all()"
```

---

## Full Documentation

- **SETUP.md** - Complete setup guide
- **README.md** - Project overview & features
- **WIREFLOW.md** - UI design & flow
- **PROJECT_PLAN.md** - Roadmap & phases

---

**Ready to get started?**

Windows: **Double-click `run.bat`**  
Or: Run the manual commands above

🎉 You'll be tracking jobs in < 2 minutes!
