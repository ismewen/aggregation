from re import finditer
from {{cookiecutter.project_slug}} import settings


def camel_case_split(identifier):
    matches = finditer('.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)', identifier)
    return [m.group(0) for m in matches]


def make_context(app, db):
    models_dict = db.class_registry

    def show_models():
        for k, model in models_dict.items():
            try:
                if issubclass(model, db.Model):
                    print(model)
            except Exception as e:
                pass

    context = dict(
        app=app,
        db=db,
        settings=settings,
        show_models=show_models,
        **models_dict
    )
    return context
