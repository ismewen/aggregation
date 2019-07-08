from functools import wraps
from typing import List, Callable

from flask import request

from aggregation import exceptions


class MethodMapper(dict):
    """
    Enables mapping HTTP methods to different ViewSet methods for a single,
    logical action.

    Example usage:

        class MyViewSet(ViewSet):

            @action(detail=False)
            def example(self, request, **kwargs):
                ...

            @example.mapping.post
            def create_example(self, request, **kwargs):
                ...
    """

    def __init__(self, action, methods):
        self.action = action
        for method in methods:
            self[method] = self.action.__name__

    def _map(self, method, func):
        assert method not in self, (
            "Method '%s' has already been mapped to '.%s'." % (method, self[method]))
        assert func.__name__ != self.action.__name__, (
            "Method mapping does not behave like the property decorator. You "
            "cannot use the same method name for each mapping declaration.")

        self[method] = func.__name__

        return func

    def get(self, func):
        return self._map('get', func)

    def post(self, func):
        return self._map('post', func)

    def put(self, func):
        return self._map('put', func)

    def patch(self, func):
        return self._map('patch', func)

    def delete(self, func):
        return self._map('delete', func)

    def head(self, func):
        return self._map('head', func)

    def options(self, func):
        return self._map('options', func)

    def trace(self, func):
        return self._map('trace', func)


def action(methods=None, detail=None, url_path=None, url_name=None, **kwargs):
    """
    Mark a ViewSet method as a routable action.

    Set the `detail` boolean to determine if this action should apply to
    instance/detail requests or collection/list requests.
    """
    methods = ['get'] if (methods is None) else methods
    methods = [method.lower() for method in methods]

    assert detail is not None, (
        "@action() missing required argument: 'detail'"
    )

    # name and suffix are mutually exclusive
    if 'name' in kwargs and 'suffix' in kwargs:
        raise TypeError("`name` and `suffix` are mutually exclusive arguments.")

    def decorator(func):
        func.mapping = MethodMapper(func, methods)

        func.detail = detail
        func.url_path = url_path if url_path else func.__name__
        func.url_name = url_name if url_name else func.__name__.replace('_', '-')
        func.kwargs = kwargs

        # Set descriptive arguments for viewsets
        if 'name' not in kwargs and 'suffix' not in kwargs:
            func.kwargs['name'] = func.__name__
        func.kwargs['description'] = func.__doc__ or None

        return func
    return decorator


def url_params_require(mandatory_params: List):

    def decorator(func):

        @wraps(func)
        def wrapper(*args, **kwargs):
            for args_name in mandatory_params:
                mandatory = dict()
                value = request.args.get(args_name, None)
                if value is None:
                    raise exceptions.RequestArgsMissing(format_kwargs=dict(args_name=args_name))
                else:
                    mandatory[args_name] = value
                setattr(request, "mandatory_params", mandatory)
            return func(*args, **kwargs)
        return wrapper

    return decorator



