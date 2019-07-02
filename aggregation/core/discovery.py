import pkgutil
from importlib import import_module

from aggregation.api import modules


def discover(name):
    for loader, module_name, is_pkg in pkgutil.walk_packages(modules.__path__, modules.__name__ + '.'):
        if name in module_name and not is_pkg:
            print(module_name)
            try:
                loader.find_module(module_name).load_module(module_name)
            except ModuleNotFoundError as e:
                print(e)


def auto_register_blueprint(app):
    for loader, module_name, is_pkg in pkgutil.walk_packages(modules.__path__, modules.__name__ + '.'):
        if 'views' in module_name and not is_pkg:
            print(module_name)
            try:
                module = loader.find_module(module_name).load_module(module_name)
                if hasattr(module, 'blueprint'):
                    app.register_blueprint(module.blueprint)
            except ModuleNotFoundError as e:
                print(e)
