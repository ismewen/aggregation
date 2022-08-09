import pkgutil

from werkzeug.utils import find_modules, import_string


def discover(name):
    from {{cookiecutter.project_slug}}.api import modules
    for loader, module_name, is_pkg in pkgutil.walk_packages(modules.__path__, modules.__name__ + '.'):
        if name in module_name and not is_pkg:
            print(module_name, is_pkg)
            try:
                loader.find_module(module_name).load_module(module_name)
            except ModuleNotFoundError as e:
                print(e)


def auto_register_blueprint(app):
    for module_name in find_modules("{{cookiecutter.project_slug}}.api.modules", recursive=True):
        if 'views' in module_name:
            try:
                module = import_string(module_name)
                if hasattr(module, 'blueprint'):
                    app.register_blueprint(module.blueprint, url_prefix="/api")
            except Exception as e:
                print(e)
        if 'models' in module_name:
            try:
                import_string(module_name)
            except Exception as e:
                print(e)
        if 'commands' in module_name:
            print(module_name)
            try:
                import_string(module_name)
            except Exception as e:
                print(e)