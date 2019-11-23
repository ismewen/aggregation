### 简介
 通过flask进行resetful接口开发有一年多, 一直使用家安大神搭建的flask框架，里面有太多值得学习的地方。结合自己学的一点皮毛，从家安的框架里面抄抄改改
 一些东西出来，搭建了一个究极破产版的flask框架。
 
 ### 基本使用
 #### 登录验证
 1. 创建oauth2client 获取 client_id && client_secret
 2. 获取token
 ```bash
 curl -u AcLh3tbouNZHjIF9wXVW1GcG:y75N0K2kfBhnq9FJr4tNVxZZXlqlDMpRw1KC8Pf5rqLpkod7 -XPOST http://127.0.0.1:5000/oauth/token -F grant_type=password -F username=username -F password=password -F scope=profile
```
结果如下
```python
{"access_token": "bqsIhN09ienftV95D9mpVbPcVq9eclMpFgEnJ0YfDt", "expires_in": 864000, "scope": "profile", "token_type": "Bearer"}
```

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


```
便会生成如下的接口,并实现基本的curd功能

`GET`, `POST` /parents/                                                                                                       
`GET`, `DELETE`, `PUT` /parents/<parent_pk>/ 

`GET`, `POST` /parents/<parent_pk>/sons/ 
`GET`, `DELETE`, `PUT` /parents/<parent_pk>/<sons>/<son_pk>/

action装饰器产生自定义的url

`GET`, `POST` /parents/list_test/                                                                                                    
`GET`, `POST` /parents/<parent_pk>/detail_test/

`GET`, `POST` /parents/<parent_pk>/sons/<son_pk>/detail_test/                                                                                 u 
`GET`, `POST` /parents/<parent_pk>/sons/list_test/

```
#### 测试用例
```python
from flask import url_for

from aggregation import db
from aggregation.core.unnittest.testcase import AggregationAuthorizedTestCase
from aggregation.api.modules.tests.tests.factorys import ParentFactory 
from aggregation.api.modules.tests.views import ParentAPIView 

class ParentTestCase(AggregationAuthorizedTestCase):
    detail_url_template = "test.{}-detail".format(ParentAPIView.__name__)
    list_url_template = "test.{}-list".format(ParentAPIView.__name__)

    def test_parent_list(self):
        parents = ParentFactory.build_batch(30)
        db.session.add_all(parents)
        db.session.commit()
        uri = url_for(self.list_url_template)
        res = self.client.get(uri)
        self.assert200(res)
        print("***" * 10)
        print(res.json)
        print("***" * 10)

    def test_parent_retrieve(self):
        parent = ParentFactory.build()
        db.session.add(parent)
        db.session.commit()
        uri = url_for(self.detail_url_template, pk=parent.id)
        res = self.client.get(uri)
        self.assert200(res)
        print("***" * 10)
        print(res.json)
        print("***" * 10)
```
#### celery支持

新建tasks.py文件
```python

from celery_app import celery

@celery.task()
def celery_test():
    print("this is an celery test")
```

启动命令参考
celery -A celery_app.celery worker -l info 
celery -A celery_app.celery beat -l info 

#### todo
1. 权限 
2. 过滤
3. ...