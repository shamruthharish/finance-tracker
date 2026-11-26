
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler(timezone="Asia/Kolkata")


def daily_budget_summary():
    """Print a daily budget summary to the console."""
    print("\n========== DAILY BUDGET SUMMARY ==========")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Budget summary job executed successfully.")
    print("==========================================\n")


def monthly_budget_alert():
    """Simulate sending a monthly budget alert email."""
    print("\n========== SIMULATED BUDGET ALERT EMAIL ==========")
    print("To: user@example.com")
    print("Subject: Monthly Budget Alert")
    print("Message: Your monthly budget summary is ready.")
    print("Email simulation completed successfully.")
    print("=================================================\n")


def start_scheduler():
    """Start background jobs if the scheduler is not running."""

    if scheduler.running:
        return

    scheduler.add_job(
        daily_budget_summary,
        trigger="cron",
        hour=9,
        minute=0,
        id="daily_budget_summary",
        replace_existing=True,
    )

    scheduler.add_job(
        monthly_budget_alert,
        trigger="cron",
        day=1,
        hour=9,
        minute=5,
        id="monthly_budget_alert",
        replace_existing=True,
    )

    scheduler.start()
    
    logger.info("Background scheduler started.")
    for job in scheduler.get_jobs():
        logger.info(
            "Scheduled job: %s | Next run: %s",
            job.id,
            job.next_run_time
        )
