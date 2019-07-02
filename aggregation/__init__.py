import logging
import logging.config
from flask import Flask
from aggregation.core.discovery import discover, auto_register_blueprint
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

    # 蓝图注册
    auto_register_blueprint(app)

    # login init
    login_manager.init_app(app)


    # babel init

    babel.init_app(app)

    return app
