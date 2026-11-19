
from flask import Flask

from app.extensions import db


def create_app(config_class=None):
    app = Flask(__name__)

    if config_class is None:
        from config import DevelopmentConfig
        config_class = DevelopmentConfig

    app.config.from_object(config_class)

    # Connect Flask-SQLAlchemy to the Flask application
    db.init_app(app)

    # Register blueprints
    from app.routes.transactions import transactions_bp
    from app.routes.budget import budget_bp

    app.register_blueprint(
        transactions_bp,
        url_prefix="/transactions"
    )

    app.register_blueprint(
        budget_bp,
        url_prefix="/budgets"
    )

    return app
