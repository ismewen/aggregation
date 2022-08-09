from flask import Blueprint

from {{cookiecutter.project_slug}}.core.decorators import action
from {{cookiecutter.project_slug}}.core.views import APIView
from {{cookiecutter.project_slug}}.api.modules.tests import schemas
from {{cookiecutter.project_slug}}.api.modules.tests import models


blueprint = Blueprint('test',
                      __name__,
                      template_folder='templates',
                      url_prefix='/test')


class ChildAPIView(APIView):
    name = "child"
    path = "/children"
    supervisor_relation = "parent"
    model = models.Child

    detail_schema = schemas.SonModelSchema

    @action(detail=True, methods=["GET","POST"])
    def detail_test(self, *args, **kwargs):
        return "hello world"

    @action(detail=False, methods=["GET", "POST"])
    def list_test(self, *args, **kwargs):
        return "hello list"


class ParentAPIView(APIView):

    name = "parent"
    path = "/parents"

    model = models.Parent

    nested_views = [
        ChildAPIView
    ]

    detail_schema = schemas.ParentModelSchema

    @action(detail=True, methods=["GET"])
    def detail_test(self, *args, **kwargs):
        return "hello world"

    @action(detail=False, methods=["GET"])
    def list_test(self, *args, **kwargs):
        return "hello list"


ParentAPIView.register_to(blueprint)
