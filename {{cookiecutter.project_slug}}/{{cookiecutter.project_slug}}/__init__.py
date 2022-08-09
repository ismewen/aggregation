import logging
import logging.config
from flask import Flask
from flask_migrate import Migrate

from {{cookiecutter.project_slug}}.core.discovery import discover, auto_register_blueprint
from {{cookiecutter.project_slug}}.core.shell import make_context
from {{cookiecutter.project_slug}}.extensions.babel import babel
from {{cookiecutter.project_slug}}.extensions.ma import ma
from {{cookiecutter.project_slug}}.extensions.db import db

__version__ = "0.0.1"


def create_app(settings):
    app = Flask(__name__)
    app.config.from_object(settings)
    db.init_app(app)

    # loggin init
    logging.config.dictConfig(config=app.config['LOGGING'])


    # marshmallow init
    ma.init_app(app)

    # discovery
    auto_register_blueprint(app)

    # babel init
    babel.init_app(app)

    # migrate init
    Migrate().init_app(app, db)

    @app.route("/")
    def hello_world():
        print("hello world")
        return "hello world"

    @app.shell_context_processor
    def make_shell_context():
        return make_context(app, db)

    return app
