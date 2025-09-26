from flask import Flask

from settings import Config
from stock_screener.models import db, migrate


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    from stock_screener.views import main
    app.register_blueprint(main)

    return app
