"""
Telegram job search command
Run this to get top 5 unseen jobs sent to Telegram
"""
from app import app, db
from models import Job, Application
import os
import requests

def send_top_jobs_to_telegram():
    """Send top 5 unseen jobs to Telegram"""
    
    with app.app_context():
        # Get jobs that don't have applications yet (unseen)
        unseen_jobs = Job.query.outerjoin(Application).filter(
            Application.id == None
        ).order_by(Job.match_score.desc()).limit(5).all()
        
        if not unseen_jobs:
            return "No new jobs available. Try running the scraper!"
        
        # Format message for Telegram
        message = "🔍 *Top 5 Jobs for You*\n\n"
        
        for i, job in enumerate(unseen_jobs, 1):
            message += f"*{i}. {job.title}*\n"
            message += f"📍 {job.company or 'Unknown Company'}"
            
            if job.location:
                message += f" | {job.location}"
            
            if job.salary_min and job.salary_max:
                message += f"\n💰 ${job.salary_min:,} - ${job.salary_max:,}"
            
            message += f"\n🎯 Match: {job.match_score}%"
            message += f"\n🔗 [View Job]({job.url})\n\n"
        
        message += "View all jobs at: http://localhost:5000"
        
        # Send to Telegram
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        chat_id = os.getenv('TELEGRAM_CHAT_ID')
        
        if not bot_token or not chat_id:
            return "Error: Telegram credentials not configured in .env"
        
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            'chat_id': chat_id,
            'text': message,
            'parse_mode': 'Markdown',
            'disable_web_page_preview': True
        }
        
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            return f"✅ Sent {len(unseen_jobs)} jobs to Telegram!"
        else:
            return f"❌ Error sending to Telegram: {response.text}"


if __name__ == '__main__':
    result = send_top_jobs_to_telegram()
    print(result)
