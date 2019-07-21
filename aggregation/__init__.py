import logging
import logging.config
from flask import Flask
import sentry_sdk
from flask_mail import Message
from sentry_sdk.integrations.flask import FlaskIntegration

from aggregation.core.discovery import discover, auto_register_blueprint, discover_remote_apps_api
from aggregation.extensions.apm import apm
from aggregation.extensions.babel import babel
from aggregation.extensions.ma import ma
from aggregation.extensions.db import db
from aggregation.extensions.login import login_manager
from aggregation.extensions.oauth import config_oauth
from aggregation.extensions.login import login_manager


def create_app(settings):
    app = Flask(__name__)
    app.config.from_object(settings)

    db.init_app(app)

    # loggin init
    logging.config.dictConfig(config=app.config['LOGGING'])

    # 授权认证
    config_oauth(app)

    # flask login init
    login_manager.init_app(app)

    # marshmallow init
    ma.init_app(app)

    # discovery
    auto_register_blueprint(app)

    discover_remote_apps_api()
    # login init
    login_manager.init_app(app)

    # babel init
    babel.init_app(app)

    # sentry init
    sentry_sdk.init(settings.SENTRY_DSN, integrations=[FlaskIntegration()])
    # mail init
    # mail.send()

    # apm init
    if settings.PRODUCTION:
        apm.init_app(app)

    @app.route("/")
    def hello_world():
        print("hello world")
        raise Exception("hello world")
        return "hello world"

    return app
