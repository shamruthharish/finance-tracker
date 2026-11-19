
from flask_sqlalchemy import SQLAlchemy

from app.database import Base

db = SQLAlchemy(model_class=Base)
