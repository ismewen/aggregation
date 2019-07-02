from flask_restful import Resource
from flask import Blueprint, url_for

from aggregation.extensions.flask_resetful_api import custom_api
from aggregation.extensions.oauth import require_oauth
from flask_restful import Api


class APIView(Resource):
    path = None  # 复数命名 such as /test
    name = None

    method_decorators = [require_oauth('profile')]
    model = None

    nested_views = [

    ]

    def get(self, *args, **kwargs):
        pass

    def post(self, *args, **kwargs):
        pass

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def register(cls, blueprint_or_app, prefix=None, flask_reset_api=None):
        flask_reset_api = flask_reset_api or Api(blueprint_or_app)

        prefix = prefix or ""
        prefix = prefix + cls.path  # /a/{}

        flask_reset_api.add_resource(cls, prefix)

        for view in cls.nested_views:
            view.register(blueprint_or_app, prefix + "/<string:{}_pk>".format(cls.name))

    @classmethod
    def get_list_url(cls):
        return url_for()
