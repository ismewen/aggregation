import copy
import itertools
from collections import OrderedDict, namedtuple
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from aggregation.core.views import APIView

Route = namedtuple('Route', ['url', 'mapping', 'name', 'detail', 'initkwargs'])
DynamicRoute = namedtuple('DynamicRoute', ['url', 'name', 'detail', 'initkwargs'])


def flatten(list_of_lists):
    """
    Takes an iterable of iterables, returns a single iterable containing all items
    """
    return itertools.chain(*list_of_lists)


@dataclass
class DynamicDetailRoute(object):
    detail: bool = True
    url: str = None
    name: str = None
    initkwargs: str = None


@dataclass
class DynamicListRoute(DynamicDetailRoute):
    detail: bool = False


class SimpleRouter(object):
    # todd endpoint 构造
    trailing_slash = '/'

    views = []

    routes = [
        # List route.
        Route(
            url=r'{prefix}{trailing_slash}',
            mapping={
                'get': 'list',
                'post': 'create'
            },
            name='{basename}-list',
            detail=False,
            initkwargs={'suffix': 'List'}
        ),
        # Dynamically generated list routes. Generated using
        # @action(detail=False) decorator on methods of the viewset
        DynamicRoute(
            url=r'{prefix}/{url_path}{trailing_slash}',
            name='{basename}-{url_name}',
            detail=False,
            initkwargs={}
        ),
        # Detail route.
        Route(
            url=r'{prefix}/{lookup}{trailing_slash}',
            mapping={
                'get': 'retrieve',
                'put': 'update',
                'delete': 'destroy'
            },
            name='{basename}-detail',
            detail=True,
            initkwargs={'suffix': 'Instance'}
        ),
        # Dynamically generated detail routes. Generated using
        # @action(detail=True) decorator on methods of the viewset.
        DynamicRoute(
            url=r'{prefix}/{lookup}/{url_path}{trailing_slash}',
            name='{basename}-{url_name}',
            detail=True,
            initkwargs={}
        ),
    ]

    @classmethod
    def escape_curly_brackets(cls, url_path):
        """
        Double brackets in regex of url_path for escape string formatting
        """
        if ('{' and '}') in url_path:
            url_path = url_path.replace('{', '{{').replace('}', '}}')
        return url_path

    def _get_dynamic_route(self, route, action):
        initkwargs = route.initkwargs.copy()
        initkwargs.update(action.kwargs)

        url_path = self.escape_curly_brackets(action.url_path)

        return Route(
            url=route.url.replace('{url_path}', url_path),
            mapping=action.mapping,
            name=route.name.replace('{url_name}', action.url_name),
            detail=route.detail,
            initkwargs=initkwargs,
        )

    def get_routes(self, api_view: 'APIView'):
        default_actions = list(flatten([route.mapping.values() for route in self.routes if isinstance(route, Route)]))
        extra_actions = api_view.get_extra_actions()

        not_allowed = [
            action.__name__ for action in extra_actions
            if action.__name__ in default_actions
        ]

        if not_allowed:
            msg = ('Cannot use the @action decorator on the following '
                   'methods, as they are existing routes: %s')
            assert not_allowed, msg % ",".join(not_allowed)

        detail_actions = [action for action in extra_actions if action.detail]
        list_actions = [action for action in extra_actions if not action.detail]

        routes = []

        for route in self.routes:
            route = copy.deepcopy(route)
            if isinstance(route, DynamicRoute) and route.detail:
                routes += [self._get_dynamic_route(route, action) for action in detail_actions]
            elif isinstance(route, DynamicRoute) and not route.detail:
                routes += [self._get_dynamic_route(route, action) for action in list_actions]
            else:
                routes.append(route)
        return routes

    @classmethod
    def get_lookup_regex(cls, api_view, lookup_prefix=''):
        base_regex = '<{pk_type}:{lookup_prefix}{lookup_url_kwarg}>{lookup_value}'
        # Use `pk` as default field, unset set.  Default regex should not
        # consume `.json` style suffixes and should break at '/' boundaries.
        lookup_field = getattr(api_view, 'lookup_field', 'pk')
        lookup_url_kwarg = getattr(api_view, 'lookup_url_kwarg', None) or lookup_field
        lookup_value = getattr(api_view, 'lookup_value_regex', '')
        return base_regex.format(
            pk_type=api_view.pk_type,
            lookup_prefix=lookup_prefix,
            lookup_url_kwarg=lookup_url_kwarg,
            lookup_value=lookup_value
        )

    @classmethod
    def get_method_map(cls, api_view, method_map):
        """
        Given a viewset, and a mapping of http methods to actions,
        return a new mapping which only includes any mappings that
        are actually implemented by the viewset.
        """
        return method_map

    @classmethod
    def get_method_view_kwargs(cls, api_view, actions, **initkwargs):
        def view(*args, **kwargs):
            self = api_view(**initkwargs)
            self.action_map = actions
            for method, action in actions.items():
                handler = getattr(self, action)
                setattr(self, method, handler)
            if hasattr(self, 'get') and not hasattr(self, 'head'):
                self.head = self.get
            return self.dispatch(*args, **kwargs)

        return view

    def get_endpoint(self, api_view, route, parent_endpoint):
        endpoint = route.name.format(basename=api_view.__name__)
        if parent_endpoint:
            return "{}:{}".format(parent_endpoint, endpoint)
        return endpoint

    @classmethod
    def get_wrapper_view(cls, api_view: 'APIView', mapping, parent_api_view):
        class WrapperView(api_view):
            pass
        setattr(WrapperView, "superior_view", parent_api_view)
        WrapperView.__name__ = cls.__name__
        for method, action in mapping.items():
            action_method = getattr(WrapperView, action)
            setattr(action_method, "action", action)
            setattr(WrapperView, method, action_method)
        return WrapperView

    @classmethod
    def get_allow_methods(cls, api_view: "APIView", route):
        if isinstance(route, Route):
            return [method.upper() for method, action in route.mapping.items() if action in api_view.allow_actions]
        return [method.upper() for method in route.mapping.keys()]

    def get_urls(self, api_view: 'APIView', parent_prefix="", parent_endpoint="", parent_api_view=None):
        routes = self.get_routes(api_view=api_view)
        prefix = api_view.path
        lookup = self.get_lookup_regex(api_view)
        urls = []
        parent_prefix = parent_prefix.lstrip("^")
        for route in routes:
            mapping = self.get_method_map(api_view, route.mapping)
            if not mapping:
                continue
            view = self.get_wrapper_view(api_view=api_view, parent_api_view=parent_api_view, mapping=mapping)
            path = route.url.format(
                prefix=parent_prefix + prefix,
                lookup=lookup,
                trailing_slash=self.trailing_slash
            )

            urls.append((
                path, dict(
                    view_func=view.as_view(view.name),
                    endpoint=self.get_endpoint(api_view, route, parent_endpoint),
                    methods=[method.upper() for method in route.mapping.keys()]
                )
            ))
        detail_route = self.routes[2]
        parent_lookup = self.get_lookup_regex(api_view=api_view, lookup_prefix="{}_".format(api_view.name))

        current_detail_prefix = detail_route.url.format(
            prefix=parent_prefix + prefix,
            lookup=parent_lookup,
            trailing_slash=self.trailing_slash
        )

        parent_prefix = parent_prefix + current_detail_prefix[:-1]
        parent_endpoint = api_view.__name__
        for nested_view in api_view.nested_views:
            nested_urls = self.get_urls(nested_view, parent_prefix, parent_endpoint,parent_api_view=api_view)
            urls.extend(nested_urls)

        return urls

    def register(self, view: 'APIView') -> None:
        self.views.append(view)


router = SimpleRouter()
