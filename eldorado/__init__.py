import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
        'DATABASE_URL',
        'mysql+pymysql://usuario:senha@localhost/eldoradodb?charset=utf8mb4'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    # Models precisam ser importados antes dos CLI/scraping
    from . import models  # noqa

    from .main import main_bp
    app.register_blueprint(main_bp)

    # registra comandos CLI de scraping
    from .scraping.cli import register_cli
    register_cli(app)

    return app
