# AI-Powered Job Search Platform

A personal job search tool that scrapes job boards, matches opportunities against your resume using AI, tracks applications, and helps you stay organized — all from a local web UI.

Built with Flask, SQLite, Tailwind CSS, and Claude AI.

---

## Features

### Multi-Board Job Scraping
- **Indeed** — Playwright-based scraper with anti-bot bypass
- **Adzuna API** — Aggregates jobs from multiple boards
- Automatic duplicate detection
- Searches are built from your job titles + keywords combined, so results are domain-specific rather than generic (e.g. "Data Analyst energy analytics" instead of just "Data Analyst")

### Search Profiles
- Save multiple named profiles (e.g. "Data Analyst", "Software Dev")
- Each profile has its own job titles, keywords, locations, job description, work experience context, and resume
- Switch the active profile with one click — scraping and AI scoring always use the active profile
- Locations are entered as individual tags (Portland OR, Salem OR, Remote, etc.)

### AI-Powered Matching
- **Match scoring** — 0-100% score for every job vs your resume (Claude Haiku)
- Scores are context-aware: your keywords and search goals are included so domain-relevant jobs score higher
- **Match explanations** — AI explains why each job matches or doesn't
- **Starred jobs** — Star any job to pin it to the top of the list as a reminder to apply

### AI Cover Letter Generation
- Personalized cover letters using your resume + job description + work experience context
- One-click generation from any job listing
- Copy to clipboard

### Application Tracking (Kanban)
- Drag-and-drop board with 6 columns: Not Applied, Applied, Interview, Rejected, Not Interested, Inactive
- Jobs auto-move to Inactive after 3 weeks
- Delete individual jobs or clear all jobs at once

### Interview Calendar
- Monthly calendar view (Sun–Sat)
- Color-coded by interview type: Phone (blue), Video (purple), Onsite (green)
- Click any day to quick-add an interview
- Upcoming interviews list

### Analytics Dashboard
- Application funnel stats
- Source and match score breakdowns

### Job List UI
- Filter by match score, location, source, or starred-only
- Sort by match score, date posted, or date scraped
- Starred jobs always float to the top regardless of sort
- Delete jobs individually with the trash icon

---

## Setup

### Prerequisites

- Python 3.8+
- Claude API key — [console.anthropic.com](https://console.anthropic.com/)
- Adzuna API credentials — [developer.adzuna.com](https://developer.adzuna.com/) (free)

### Installation

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Install Playwright browsers** (for Indeed scraping):
   ```bash
   python -m playwright install
   ```

3. **Create a `.env` file** with:
   ```
   CLAUDE_API_KEY=sk-ant-...
   ADZUNA_APP_ID=your_app_id
   ADZUNA_APP_KEY=your_api_key
   SECRET_KEY=any-random-string
   ```

4. **Initialize the database:**
   ```bash
   flask init-db
   python migrate_db.py
   ```

5. **Run:**
   ```bash
   python app.py
   ```

6. **Open** `http://localhost:5000`

---

## Usage

### First-time setup

1. Go to **Settings**
2. Upload your resume (PDF or DOCX)
3. Fill in your search profile:
   - **Profile name** (e.g. "Data Analyst")
   - **Job titles** — comma-separated (e.g. `Data Analyst, Data Engineer`)
   - **Locations** — add each as a tag (Portland OR, Remote, etc.)
   - **Keywords** — specific terms that matter to you (e.g. `energy analytics, Inflation Reduction Act, AI`)
   - **Job description** — plain English description of what you're looking for
   - **Work experience** — background context the AI uses for scoring and cover letters
4. Create additional profiles if you're targeting different roles

### Finding jobs

1. Go to **Jobs** tab
2. Click **Scrape Indeed** or **Scrape Adzuna**
3. Jobs appear sorted by match score with the active profile's resume and keywords factored in
4. Star promising jobs (★) to pin them to the top as reminders

### Applying

1. Click a job title to view details
2. Read the AI match explanation
3. Generate a cover letter with one click
4. Mark as Applied — it moves to the Kanban board

### Tracking

- **Applications** tab — drag cards between columns as status changes
- **Calendar** tab — schedule and view interviews

---

## Project Structure

```
job_search_platform/
├── app.py                    # Main Flask application & all routes
├── models.py                 # Database models (Job, Application, Resume, SearchPreferences, Interview)
├── config.py                 # Configuration
├── requirements.txt
│
├── ai/
│   ├── job_matcher.py        # Match scoring & explanations (Claude Haiku)
│   ├── cover_letter.py       # Cover letter generation (Claude Sonnet)
│   └── resume_parser.py      # PDF/DOCX text extraction
│
├── scrapers/
│   ├── base.py               # Base scraper interface
│   ├── indeed_playwright.py  # Indeed (Playwright)
│   └── adzuna_api.py         # Adzuna REST API
│
├── templates/
│   ├── base.html
│   ├── index.html            # Job listings
│   ├── job_detail.html       # Job detail + cover letter + match analysis
│   ├── applications.html     # Kanban board
│   ├── calendar.html         # Interview calendar
│   ├── analytics.html        # Analytics dashboard
│   └── settings.html         # Profiles, resume, preferences
│
└── static/
    ├── js/
    │   ├── notifications.js  # Toast system
    │   └── loading.js        # Loading overlay
    └── uploads/              # Resume files (gitignored)
```

---

## API Costs (approximate)

| Task | Model | Cost per 100 jobs |
|------|-------|-------------------|
| Match scoring | Claude Haiku | ~$0.20 |
| Cover letters (per letter) | Claude Sonnet | ~$0.03 |

Light personal usage runs well under $5/month.

---

## Troubleshooting

**Indeed scraper not working** — Run `python -m playwright install`

**Adzuna returns 0 jobs** — Check `.env` credentials and location format

**No AI match scores** — Upload a resume in Settings and verify `CLAUDE_API_KEY` is set

**Cover letter fails** — Confirm API key starts with `sk-ant-`

**Database errors** — Run `flask init-db` then `python migrate_db.py`

**Calendar days misaligned** — Fixed as of current version (Sun–Sat, not Mon–Sun)

---

## License

MIT — see `LICENSE`
