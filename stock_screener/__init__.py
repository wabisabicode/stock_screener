from flask import Flask

from settings import Config
from stock_screener.models import db, migrate


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    from stock_screener.routes.main import main_bp
    app.register_blueprint(main_bp)

    from stock_screener.cli import (add_tickers_command, stocks_cli,
                                    update_stocks)
    app.cli.add_command(add_tickers_command)
    app.cli.add_command(update_stocks)
    app.cli.add_command(stocks_cli)

    return app
