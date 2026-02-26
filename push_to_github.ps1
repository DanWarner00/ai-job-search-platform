# Quick GitHub Push Script
# Run this after creating your GitHub repository

Write-Host "🚀 Job Search Platform - GitHub Setup" -ForegroundColor Cyan
Write-Host "=" * 50
Write-Host ""

# Check if git is installed
$gitInstalled = Get-Command git -ErrorAction SilentlyContinue
if (-not $gitInstalled) {
    Write-Host "❌ Git is not installed!" -ForegroundColor Red
    Write-Host "   Download from: https://git-scm.com/download/win"
    exit 1
}

Write-Host "✅ Git found" -ForegroundColor Green

# Check if in correct directory
if (-not (Test-Path "app.py")) {
    Write-Host "❌ Not in project directory!" -ForegroundColor Red
    Write-Host "   Run this script from C:\job_search_platform\"
    exit 1
}

Write-Host "✅ Project directory confirmed" -ForegroundColor Green
Write-Host ""

# Get GitHub username and repo name
Write-Host "Enter your GitHub details:" -ForegroundColor Yellow
$username = Read-Host "GitHub username"
$reponame = Read-Host "Repository name (default: ai-job-search-platform)"

if ([string]::IsNullOrWhiteSpace($reponame)) {
    $reponame = "ai-job-search-platform"
}

Write-Host ""
Write-Host "Repository will be: https://github.com/$username/$reponame" -ForegroundColor Cyan
$confirm = Read-Host "Continue? (y/n)"

if ($confirm -ne "y") {
    Write-Host "Cancelled." -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "🔧 Setting up Git..." -ForegroundColor Cyan

# Initialize git if needed
if (-not (Test-Path ".git")) {
    Write-Host "Initializing git repository..."
    git init
}

# Add all files
Write-Host "Adding files..."
git add .

# Show what will be committed
Write-Host ""
Write-Host "📁 Files to commit:" -ForegroundColor Yellow
git status --short

Write-Host ""
Write-Host "⚠️  SECURITY CHECK:" -ForegroundColor Yellow
Write-Host "Verify these files are NOT listed above:" -ForegroundColor Yellow
Write-Host "  ❌ .env (API keys)"
Write-Host "  ❌ jobs.db (your data)"
Write-Host "  ❌ static/uploads/*.pdf (your resume)"
Write-Host ""

$continue = Read-Host "Files look good? (y/n)"
if ($continue -ne "y") {
    Write-Host "Cancelled. Check .gitignore file." -ForegroundColor Yellow
    exit 0
}

# Create initial commit
Write-Host ""
Write-Host "Creating initial commit..."
git commit -m "Initial commit: AI-powered job search platform

Features:
- Multi-board job scraping (Indeed + Adzuna)
- AI resume matching with Claude
- AI-generated cover letters
- Kanban application tracking
- Interview calendar
- Modern dark UI"

# Add remote
Write-Host "Adding GitHub remote..."
git remote add origin "https://github.com/$username/$reponame.git"

# Rename branch to main
git branch -M main

# Push to GitHub
Write-Host ""
Write-Host "🚀 Pushing to GitHub..." -ForegroundColor Cyan
Write-Host "   You may be prompted for GitHub credentials"
Write-Host "   Password = Personal Access Token (not your GitHub password!)"
Write-Host ""

git push -u origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "=" * 50 -ForegroundColor Green
    Write-Host "✅ SUCCESS!" -ForegroundColor Green
    Write-Host "=" * 50 -ForegroundColor Green
    Write-Host ""
    Write-Host "Your project is now on GitHub:" -ForegroundColor Cyan
    Write-Host "https://github.com/$username/$reponame" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "  1. Visit the URL above to see your repo"
    Write-Host "  2. Add topics: python, flask, ai, job-search, claude"
    Write-Host "  3. Add description in About section"
    Write-Host "  4. (Optional) Add screenshots"
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "❌ Push failed!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Common issues:" -ForegroundColor Yellow
    Write-Host "  • Repository doesn't exist on GitHub → Create it first"
    Write-Host "  • Wrong credentials → Use Personal Access Token"
    Write-Host "  • Already exists → Use 'git push --force' (careful!)"
    Write-Host ""
    Write-Host "See setup_github.md for detailed instructions"
}
