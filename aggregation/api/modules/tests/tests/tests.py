from flask import url_for

from aggregation import db
from aggregation.core.unnittest.testcase import AggregationAuthorizedTestCase
from aggregation.api.modules.tests.tests.factorys import ParentFactory, ChildFactory
from aggregation.api.modules.tests.views import ParentAPIView, ChildAPIView
from aggregation.api.modules.tests.schemas import ParentModelSchema, SonModelSchema


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

    def test_parent_update(self):
        parent = ParentFactory.build()
        db.session.add(parent)
        db.session.commit()
        print("\n" * 4)
        print("before update: %s" % parent.name)
        uri = url_for(self.detail_url_template, pk=parent.id)
        res = self.client.put(uri, json={"name": "wenjun"})
        print(res.json)
        print(type(res.json))
        print("\n" * 4)

    def test_parent_destroy(self):
        parent = ParentFactory.build()
        db.session.add(parent)
        db.session.commit()
        print("\n" * 4)
        print("before update: %s" % parent.name)
        uri = url_for(self.detail_url_template, pk=parent.id)
        res = self.client.delete(uri)
        self.assertEqual(res.status_code, 204)
        res = self.client.get(uri)
        self.assertEqual(res.status_code, 400)
        print(res.json)
        print(type(res.json))
        print("\n" * 4)

    def test_parent_create(self):
        parent = ParentFactory.build()
        res = ParentModelSchema().dump(parent).data
        res.pop("id")
        res = self.client.post(url_for(self.list_url_template), json=res)
        self.assertEqual(res.status_code, 201)

    def test_parent_detail_action(self):
        obj = ParentFactory()
        db.session.add(obj)
        db.session.commit()
        url = url_for("test.ParentAPIView-detail-test", pk=obj.id)
        res = self.client.get(url)
        self.assert200(res)

    def test_parent_list_action(self):
        url = url_for("test.ParentAPIView-list-test")
        res = self.client.get(url)
        self.assert200(res)


class SonTestCase(AggregationAuthorizedTestCase):
    detail_url_endpoint = "test.ParentAPIView:ChildAPIView-detail"
    list_url_endpoint = "test.ParentAPIView:ChildAPIView-list"

    def test_children_list(self):
        parent = ParentFactory()
        children = ChildFactory.build_batch(10, parent=parent)
        db.session.add(parent)
        db.session.add_all(children)
        db.session.commit()
        url = url_for(self.list_url_endpoint, parent_pk=parent.id)
        res = self.client.get(url)
        self.assert200(res)
        url = url_for(self.list_url_endpoint, parent_pk=23)
        res = self.client.get(url)
        self.assertEqual(res.status_code, 400)

    def test_children_detail(self):
        parent = ParentFactory()
        child = ChildFactory(parent=parent)
        db.session.add(child)
        db.session.commit()
        url = url_for(self.detail_url_endpoint, pk=child.id, parent_pk=parent.id)
        res = self.client.get(url)
        self.assert200(res)
        print(res.json)

    def test_children_update(self):
        parent = ParentFactory()
        child = ChildFactory(parent=parent)
        db.session.add(child)
        db.session.commit()
        url = url_for(self.detail_url_endpoint, pk=child.id, parent_pk=parent.id)
        res = self.client.put(url, json={"name": "wenjun"})
        self.assert200(res)
        self.assertEqual(res.json.get("name"), "wenjun")

    def test_children_delete(self):
        parent = ParentFactory()
        child = ChildFactory(parent=parent)
        db.session.add(child)
        db.session.commit()
        url = url_for(self.detail_url_endpoint, pk=child.id, parent_pk=parent.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, 204)

    def test_children_create(self):
        parent = ParentFactory()
        db.session.add(parent)
        db.session.commit()
        url = url_for(self.list_url_endpoint, parent_pk=parent.id)
        res = self.client.post(url, json={"name": "ismewen"})
        self.assertEqual(res.status_code, 201)
        self.assertEqual(res.json.get("name"), "ismewen")

    def test_children_detail_action(self):
        parent = ParentFactory()
        child = ChildFactory(parent=parent)
        db.session.add(child)
        db.session.commit()
        endpoint = "test.ParentAPIView:ChildAPIView-detail-test"
        url = url_for(endpoint, pk=child.id, parent_pk=parent.id)
        res = self.client.get(url)
        print(res.data)
        self.assertEqual(res.status_code, 200)
        res = self.client.post(url)
        print(res.data)
        self.assertEqual(res.status_code, 200)

    def test_children_list_action(self):
        parent = ParentFactory()
        child = ChildFactory(parent=parent)
        db.session.add(child)
        db.session.commit()
        endpoint = "test.ParentAPIView:ChildAPIView-list-test"
        url = url_for(endpoint, parent_pk=parent.id)
        res = self.client.get(url)
        print(res.data)
        self.assertEqual(res.status_code, 200)
        res = self.client.post(url)
        print(res.data)
        self.assertEqual(res.status_code, 200)




