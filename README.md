### 简介
 通过flask进行resetful接口开发有一年多, 一直使用家安大神搭建的flask框架，里面有太多值得学习的地方。结合自己学的一点皮毛，从家安的框架里面抄抄改改
 一些东西出来，搭建了一个究极破产版的flask框架。
 
 ### 基本使用
 
 #### apiview的基本用法
```python
from flask import Blueprint

from aggregation.core.decorators import action
from aggregation.core.views import APIView
from aggregation.api.modules.tests import schemas
from aggregation.api.modules.tests import models


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
``` 
 
