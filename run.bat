@echo off
echo ========================================
echo Job Search Platform - Quick Start
echo ========================================
echo.

REM Check if venv exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
    echo.
)

REM Activate venv
echo Activating virtual environment...
call venv\Scripts\activate
echo.

REM Check if requirements are installed
if not exist "venv\Lib\site-packages\flask\" (
    echo Installing dependencies...
    pip install -r requirements.txt
    echo.
)

REM Check if .env exists
if not exist ".env" (
    echo Creating .env file from template...
    copy .env.example .env
    echo.
    echo ⚠️  IMPORTANT: Edit .env file with your API keys!
    echo    - CLAUDE_API_KEY (required for AI features)
    echo.
    pause
)

REM Create uploads directory
if not exist "static\uploads\" (
    mkdir static\uploads
)

REM Initialize database if needed
if not exist "jobs.db" (
    echo Initializing database...
    python -c "from app import db, app; app.app_context().push(); db.create_all(); print('✅ Database created!')"
    echo.
)

REM Run the app
echo ========================================
echo Starting Flask application...
echo Visit: http://localhost:5000
echo Press Ctrl+C to stop
echo ========================================
echo.

python app.py
