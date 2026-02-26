# 🎯 AI-Powered Job Search Platform

A full-stack web application that automates job searching with AI-powered resume matching, cover letter generation, and application tracking.

Built with Flask, SQLite, Tailwind CSS, and Claude AI.

---

## ✨ Features

### 🔍 **Multi-Board Job Scraping**
- **Indeed** - Playwright-based scraper with anti-bot detection bypass
- **Adzuna API** - Aggregates jobs from Indeed, Monster, CareerBuilder, Dice, and more
- Automatic duplicate detection
- Configurable search preferences (job titles, keywords, locations)

### 🤖 **AI-Powered Matching**
- **Resume parsing** - Upload PDF/DOCX resume
- **Match scoring** - 0-100% match score vs your resume (Claude 3.5 Haiku)
- **Match explanations** - AI explains why each job matches your skills
- **Smart filtering** - Filter by match score, location, source
- **Cost-optimized** - Uses Haiku for scoring (5x cheaper), Sonnet for cover letters

### 📝 **AI Cover Letter Generation**
- **Personalized letters** - Generated with Claude Sonnet 4.5
- **Context-aware** - Uses your resume + job description + search preferences
- **One-click generation** - From any job listing
- **Copy to clipboard** - Quick export

### 📊 **Application Tracking**
- **Kanban board** - Drag-and-drop interface with 6 statuses:
  - Not Applied
  - Applied
  - Interview
  - Rejected
  - Not Interested (for AI learning)
  - Inactive (auto-populated after 3 weeks)
- **Status tracking** - Automatic date tracking
- **Notes** - Add notes to each application

### 📅 **Interview Calendar**
- **Monthly calendar view** - See all scheduled interviews
- **Color-coded** - Phone (blue), Video (purple), Onsite (green)
- **Quick add** - Click any day to schedule
- **Upcoming list** - All future interviews in one view
- **Linked to jobs** - Each interview links back to job posting

### 📈 **Analytics Dashboard**
- Application funnel visualization
- Success rate tracking
- Source performance metrics

### 🎨 **Modern Dark UI**
- Tailwind CSS styling
- Toast notifications (no alert popups!)
- Loading overlays
- Smooth transitions and hover effects
- Gradient buttons with icons
- Fully responsive

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- pip
- Claude API key ([Get one here](https://console.anthropic.com/))
- Adzuna API credentials ([Free signup](https://developer.adzuna.com/))

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/job-search-platform.git
   cd job-search-platform
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Playwright browsers:**
   ```bash
   python -m playwright install
   ```

4. **Configure environment variables:**
   ```bash
   cp .env.example .env
   ```

   Edit `.env` and add:
   - `CLAUDE_API_KEY` - Your Claude API key
   - `ADZUNA_APP_ID` - Your Adzuna app ID
   - `ADZUNA_APP_KEY` - Your Adzuna API key
   - (Optional) Telegram credentials for notifications

5. **Initialize database:**
   ```bash
   flask init-db
   ```

6. **Run the application:**
   ```bash
   python app.py
   ```

7. **Open in browser:**
   ```
   http://localhost:5000
   ```

---

## 📖 Usage

### 1. Initial Setup

1. Go to **Settings** tab
2. **Upload your resume** (PDF or DOCX)
3. **Configure search preferences:**
   - Job titles (e.g., "Data Analyst, Python Developer")
   - Keywords (e.g., "Python, SQL, Machine Learning")
   - Locations (e.g., "Portland, OR, Remote")
   - Optional: Salary range, job description

### 2. Find Jobs

1. Go to **Jobs** tab
2. Click **"Scrape Indeed"** or **"Scrape Adzuna"**
3. Wait for jobs to load (AI scoring happens automatically)
4. Browse jobs sorted by match score

### 3. Apply to Jobs

1. Click any job to view details
2. See AI match explanation
3. Click **"Generate Cover Letter"** for AI-written cover letter
4. Click **"Apply on Indeed"** to apply
5. Click **"Mark as Applied"** to track

### 4. Track Applications

1. Go to **Applications** tab
2. See Kanban board with all applications
3. Drag cards between columns as status changes
4. Click **"Schedule Interview"** when you get one

### 5. Manage Interviews

1. Go to **Calendar** tab
2. Click **"+ Add Interview"** or click any day
3. Fill in details (date, time, type, notes)
4. View all upcoming interviews

---

## 🛠️ Tech Stack

### Backend
- **Flask** - Web framework
- **SQLAlchemy** - ORM
- **SQLite** - Database (development)
- **Playwright** - Web scraping (Indeed)
- **Requests** - API calls (Adzuna)

### AI/ML
- **Claude 3.5 Haiku** - Match scoring & explanations (cost-optimized)
- **Claude Sonnet 4.5** - Cover letter generation (premium quality)
- **PyPDF2** - Resume parsing
- **Anthropic SDK** - Claude API integration

### Frontend
- **Tailwind CSS** - Styling
- **Alpine.js** - Lightweight interactivity
- **Custom JS** - Toast notifications, loading states
- **Dark mode** - Full dark theme

---

## 📁 Project Structure

```
job_search_platform/
├── app.py                      # Main Flask application
├── models.py                   # Database models
├── config.py                   # Configuration classes
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
├── .gitignore                 # Git ignore rules
│
├── ai/                        # AI modules
│   ├── resume_parser.py       # Parse PDF/DOCX resumes
│   ├── job_matcher.py         # Calculate match scores
│   └── cover_letter.py        # Generate cover letters
│
├── scrapers/                  # Job board scrapers
│   ├── base.py               # Base scraper class
│   ├── indeed_playwright.py  # Indeed scraper
│   └── adzuna_api.py         # Adzuna API scraper
│
├── templates/                 # HTML templates
│   ├── base.html             # Base template
│   ├── index.html            # Job listings
│   ├── job_detail.html       # Job detail page
│   ├── applications.html     # Kanban board
│   ├── calendar.html         # Interview calendar
│   ├── analytics.html        # Analytics dashboard
│   └── settings.html         # Settings page
│
├── static/                    # Static assets
│   ├── js/
│   │   ├── notifications.js  # Toast notification system
│   │   └── loading.js        # Loading overlay system
│   └── uploads/              # Resume uploads (gitignored)
│
└── docs/                      # Documentation
    ├── WIREFLOW.md           # UI/UX wireframes
    ├── PROJECT_PLAN.md       # Development roadmap
    ├── AI_LEARNING.md        # AI learning strategy
    ├── AI_MODELS.md          # Model selection & costs
    ├── ADZUNA_SETUP.md       # Adzuna API setup
    ├── FEATURES_STATUS.md    # Feature completion status
    └── IMPROVEMENTS.md       # UX improvements log
```

---

## 💰 API Costs

### Cost per 100 Jobs Scraped

| Task | Model | Cost |
|------|-------|------|
| Match scoring (100 jobs) | Haiku | $0.20 |
| Cover letters (10 jobs) | Sonnet | $0.30 |
| **Total** | Mixed | **$0.50** |

### Monthly Estimates

- **Light usage** (10 jobs/day): ~$1.20/month
- **Medium usage** (50 jobs/day): ~$4.20/month
- **Heavy usage** (200 jobs/day): ~$14.40/month

See `AI_MODELS.md` for detailed cost breakdown and optimization tips.

---

## 🔧 Configuration

### AI Model Selection

Edit `ai/job_matcher.py` and `ai/cover_letter.py` to change models:

**Current setup (optimized):**
- Match scoring: `claude-3-5-haiku-20241022` (cheap & fast)
- Cover letters: `claude-3-5-sonnet-20241022` (premium quality)

**To use cheaper models:**
```python
# In job_matcher.py
model="claude-3-haiku-20240307"  # Older Haiku (even cheaper)
```

**To use better models:**
```python
# In cover_letter.py
model="claude-opus-4-20250514"  # Opus (best quality, expensive)
```

### Database

**Development:** SQLite (`jobs.db`)

**Production:** PostgreSQL
```python
# config.py
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://user:pass@localhost/jobsearch')
```

---

## 🎯 Roadmap

### ✅ Completed
- Multi-board job scraping (Indeed + Adzuna)
- AI resume matching with explanations
- AI cover letter generation
- Kanban application tracking
- Interview calendar
- Analytics dashboard
- Modern dark UI with polish

### 🚧 In Progress
- Company research chat bot
- AI learning from rejected jobs

### 📋 Planned
- Gmail integration (auto-track responses)
- Telegram daily briefing
- LinkedIn/ZipRecruiter scrapers
- Similar jobs recommendation
- Weekly goals tracking
- Email tracking UI

See `FEATURES_STATUS.md` for detailed status.

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📝 License

MIT License - See `LICENSE` file for details

---

## 🙏 Acknowledgments

- **OpenClaw** - AI framework used for development
- **Anthropic Claude** - AI model powering match scoring & cover letters
- **Adzuna** - Job aggregation API
- **Tailwind CSS** - UI styling
- **Playwright** - Web scraping

---

## 📧 Contact

**Author:** Daniel  
**Location:** Portland, OR  
**Built with:** Python, Flask, Claude AI, OpenClaw

---

## 🐛 Troubleshooting

### "Indeed scraper not working"
→ Install Playwright browsers: `python -m playwright install`

### "Adzuna returns 0 jobs"
→ Check API credentials in `.env`, verify location format

### "No AI match scores"
→ Upload resume in Settings, check Claude API key

### "Cover letter generation fails"
→ Verify Claude API key is correct (starts with `sk-ant-api03-`)

### "Database errors"
→ Run `flask init-db` to recreate database

---

## 📚 Documentation

- **Full docs:** See `/docs` folder
- **API costs:** `AI_MODELS.md`
- **Features:** `FEATURES_STATUS.md`
- **Setup:** `ADZUNA_SETUP.md`

---

## ⭐ Star this repo if it helped you land a job!
