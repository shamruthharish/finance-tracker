
from flask import Flask
from app.extensions import db, login_manager


def create_app(config_class=None):
    app = Flask(__name__)

    if config_class is None:
        from config import DevelopmentConfig
        config_class = DevelopmentConfig

    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)

    from app.database import User

    @login_manager.user_loader
    def load_user(user_id):
        try:
            return db.session.get(User, int(user_id))
        except (ValueError, TypeError):
            return None

    from app.routes.transactions import transactions_bp
    from app.routes.budget import budget_bp
    from app.routes.auth import auth_bp

    app.register_blueprint(
        transactions_bp,
        url_prefix="/transactions"
    )

    app.register_blueprint(
        budget_bp,
        url_prefix="/budgets"
    )

    app.register_blueprint(auth_bp)

    return app
