from re import finditer

from aggregation import db
from flask import current_app


def camel_case_split(identifier):
    matches = finditer('.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)', identifier)
    return [m.group(0) for m in matches]


def make_context():
    models_dict = db.class_registry

    def show_models():
        for k, model in models_dict.items():
            try:
                if issubclass(model, db.Model):
                    print(model)
            except Exception as e:
                pass

    context = dict(
        app=current_app,
        db=db,
        show_models=show_models,
        **models_dict
    )
    return context
