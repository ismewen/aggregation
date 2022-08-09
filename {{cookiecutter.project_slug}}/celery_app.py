import pkgutil

from celery import Celery
from flask import current_app

import {{cookiecutter.project_slug}}.api.modules
from {{cookiecutter.project_slug}} import create_app
from {{cookiecutter.project_slug}} import settings

if not current_app:
    app = create_app(settings)
else:
    app = current_app


def create_celery(app):
    _celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    _celery.conf.update(app.config)

    class ContextTask(_celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                # is need to add request context?
                return self.run(*args, **kwargs)
    setattr(_celery, "Task", ContextTask)
    return _celery


celery = create_celery(app)

modules = [x[1] for x in pkgutil.walk_packages({{cookiecutter.project_slug}}.api.modules.__path__, prefix='aggregation.api.modules.')]
celery.autodiscover_tasks(modules)
