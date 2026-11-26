
import os

from flask import Flask, redirect, url_for
from app.extensions import db, login_manager, csrf


def create_app(config_class=None):

    app = Flask(__name__)

    if config_class is None:
        from config import DevelopmentConfig
        config_class = DevelopmentConfig

    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)

    from app.database import User

    @login_manager.user_loader
    def load_user(user_id):
        try:
            return db.session.get(User, int(user_id))
        except (ValueError, TypeError):
            return None

    csrf.init_app(app)

    # Import blueprints
    from app.routes.transactions import transactions_bp
    from app.routes.budget import budget_bp
    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.file_operations import file_bp
    from app.routes.api import api_bp

    # Register blueprints
    app.register_blueprint(dashboard_bp)

    app.register_blueprint(
        transactions_bp,
        url_prefix="/transactions"
    )

    app.register_blueprint(
        budget_bp,
        url_prefix="/budgets"
    )

    app.register_blueprint(auth_bp)

    # Day 16: CSV Import and Export
    app.register_blueprint(file_bp)
    app.register_blueprint(api_bp)
    @app.route("/")
    def home():
        return redirect(url_for("dashboard.dashboard"))

    # Day 18: Start background scheduler
    
    # Day 18: Start background scheduler
    from app.tasks.scheduler import start_scheduler, scheduler

    should_start_scheduler = (
        not app.testing
        and (
            not app.debug
            or os.environ.get("WERKZEUG_RUN_MAIN") == "true"
        )
    )

    if should_start_scheduler:
        start_scheduler()

        app.logger.info("Background scheduler initialized.")

        for job in scheduler.get_jobs():
            app.logger.info(
                "Scheduled job: %s | Next run: %s",
                job.id,
                job.next_run_time
            )
    return app
