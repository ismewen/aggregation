import copy
from inspect import getmembers

from flask import request, url_for, jsonify, make_response
from flask.views import MethodView
from flask_marshmallow import Schema
from flask_sqlalchemy import Pagination

from {{cookiecutter.project_slug}} import db, exceptions, ma
from {{cookiecutter.project_slug}}.core.proxy import current_action
from {{cookiecutter.project_slug}}.core.routers import router

DEFAULT_ACTIONS = ["list", "retrieve", 'destroy', 'create', 'update']


class APIView(MethodView):
    name: str = None
    path: str = None

    model: type(db.Model) = None
    nested_views = []
    supervisor_relation: str = None

    detail_schema: type(ma.Schema) = None
    schema_mapping: dict = {}  # action:schema

    allow_actions = ["list", "retrieve", 'destroy', 'create', 'update']

    pk_type: str = 'int'
    lookup_field: str = "pk"
    primary_key: str = "id"

    page: int = 1
    per_page: int = 20
    paginator_enabled: bool = True

    # decorators = [require_oauth.acquire('basic')]

    @classmethod
    def _cast(cls, to_type, value, field):
        try:
            return to_type(value)
        except ValueError:
            raise exceptions.IllegalValueForField(format_kwargs={'field': field})

    def dispatch_request(self, *args, **kwargs):

        def rollback():
            try:
                db.session.rollback()
            except Exception as ex:
                print(ex)
                pass

        try:
            method = getattr(self, request.method.lower(), None)
            if method.action in DEFAULT_ACTIONS and method.action not in self.allow_actions:
                raise exceptions.MethodNotAllowed()
            setattr(request, "action", method.action)
            result = super(APIView, self).dispatch_request(*args, **kwargs)
            if isinstance(result, tuple) and len(result) == 2:
                # todo
                data = {
                    "result": True,
                    "code": 200,
                    "data": result[0],
                    "msg": "",
                }
                return make_response(jsonify(data), result[1])
            data = {
                "result": True,
                "code": 200,
                "data": result,
                "msg": "",
            }
            return jsonify(data)
        except exceptions.HMTGeneralAPIError as e:
            rollback()
            return e.json_response(), e.status

    @classmethod
    def get_router(cls):
        return router

    def get_model(self):
        return self.model

    def get_schema(self) -> type(Schema):
        schema = self.schema_mapping.get(current_action, None) or self.schema_mapping.get("default")
        schema = schema or self.detail_schema
        return schema

    @classmethod
    def _is_extra_action(cls, attr):
        return hasattr(attr, 'mapping')

    @classmethod
    def get_extra_actions(cls):
        """
        Get the methods that are marked as an extra ViewSet `@action`.
        """
        return [method for _, method in getmembers(cls, cls._is_extra_action)]

    @classmethod
    def register_to(cls, blueprint_or_app):
        view_router = cls.get_router()
        urls = view_router.get_urls(cls)
        for rule, kwargs in urls:
            blueprint_or_app.add_url_rule(rule=rule, **kwargs)

    @classmethod
    def get_supervisor_view_kwargs(cls, superior_view, **kwargs):
        superior_kwargs = copy.deepcopy(kwargs)
        superior_kwargs["pk"] = superior_kwargs["{}_pk".format(superior_view.name)]
        return superior_kwargs

    def has_supervisor(self):
        return getattr(self, "superior_view", False)

    def get_supervisor_obj(self, *args, **kwargs):
        superior_obj = None
        if self.has_supervisor():
            # 存在上级接口
            superior_kwargs = self.get_supervisor_view_kwargs(superior_view=self.superior_view, **kwargs)
            superior_obj = self.superior_view().get_object(**superior_kwargs)
        if not superior_obj:
            raise exceptions.ObjectNotFoundError()
        return superior_obj

    def before_serialize_many(self, query):
        return query

    def get_query(self, enable_filter=True, *args, **kwargs):
        query = self.get_model().query
        if self.has_supervisor():
            supervisor_obj = self.get_supervisor_obj(*args, **kwargs)
            query = query.filter(
                getattr(self.model, self.supervisor_relation) == supervisor_obj
            )
        if enable_filter:
            # 添加过滤，supervisor 获取的时候设置enable_filter为false
            pass
        return query

    def get_object(self, pk, enable_filter=True, raise_404=True, *args, **kwargs):
        query = self.get_query(enable_filter=enable_filter, *args, **kwargs)
        obj = query.filter(getattr(self.get_model(), getattr(self, 'primary_key')) == pk).first()
        if raise_404 and not obj:
            raise exceptions.ObjectNotFoundError()
        return obj

    def new_object(self, *args, **kwargs):
        schema = self.get_schema()
        s = schema()
        data = request.get_json(silent=True)
        obj, errors = s.load(data)
        if errors:
            raise exceptions.SchemaValidationError()
        db.session.add(obj)
        if self.has_supervisor():
            # 存在上级接口
            superior_obj = self.get_supervisor_obj(*args, **kwargs)
            setattr(obj, self.supervisor_relation, superior_obj)
        return obj

    # hooks
    def before_obj_created(self, obj):
        pass

    def after_obj_created(self, obj):
        pass

    def before_obj_updated(self, obj):
        pass

    def after_obj_updated(self, obj):
        pass

    def before_obj_deleted(self, obj):
        pass

    def after_obj_deleted(self, obj):
        pass

    def after_retrieve(self, obj, *args, **kwargs):
        pass

    def get_pagination_params(self):
        page = self._cast(int, request.args.get("page", self.page), "page")
        per_page = self._cast(int, request.args.get("per_page", self.per_page), "per_page")
        return page, per_page

    @classmethod
    def paginator(cls, paginator: Pagination):
        page, per_page = paginator.page, paginator.per_page
        prev, _next = None, None
        kwargs = copy.copy(dict(request.args))
        if "page" in kwargs:
            kwargs.pop("page")
        if "per_page" in kwargs:
            kwargs.pop("per_page")
        if paginator.has_next:
            _next = url_for(request.endpoint, page=page + 1, per_page=per_page, **kwargs)
        if paginator.has_prev:
            prev = url_for(request.endpoint, page=page - 1, per_page=per_page, **kwargs)
        return prev, _next

    # http actions

    def create(self, *args, **kwargs):
        obj = self.new_object(*args, **kwargs)
        try:
            db.session.flush()
            self.before_obj_created(obj)
            db.session.commit()
            self.after_obj_created(obj)
        except Exception as e:
            raise exceptions.SqlalchemyCommitError(format_kwargs=dict(error_message=e.message))
        return self.detail_schema().dump(obj).data, 201

    def update(self, pk, *args, **kwargs):
        obj = self.get_object(pk, *args, **kwargs)
        update_schema = self.get_schema()
        payload = request.get_json(silent=True)
        self.before_obj_updated(obj)
        result = update_schema().load(payload, session=db.session, instance=obj)
        if result.errors:
            raise exceptions.SchemaValidationError(errors=result.errors)
        obj = result.data
        try:
            db.session.commit()
        except Exception as e:
            raise exceptions.SqlalchemyCommitError(str(e))
        return self.detail_schema().dump(obj).data, 200

    def destroy(self, pk, *args, **kwargs):
        obj = self.get_object(pk, *args, **kwargs)
        self.before_obj_deleted(obj)
        db.session.delete(obj)
        try:
            db.session.commit()
        except Exception as e:
            raise exceptions.SqlalchemyCommitError(str(e))
        self.after_obj_deleted(obj)
        res = self.detail_schema().dump(obj, many=False).data, 204
        return res

    def list(self, *args, **kwargs):
        query = self.get_query(*args, **kwargs)
        query = self.before_serialize_many(query)
        schema = self.get_schema()()
        if self.paginator_enabled:
            page, per_page = self.get_pagination_params()
            paginator = query.paginate(page=page, per_page=per_page)
            items = paginator.items
        else:
            items = query.all()
        ret = {
            'total': query.count(),
            "results": schema.dump(items, many=True)
        }
        return ret, 200

    def retrieve(self, pk, *args, **kwargs):
        obj = self.get_object(pk, *args, **kwargs)
        self.after_retrieve(obj, *args, **kwargs)
        schema = self.get_schema()()
        return schema.dump(obj, many=False), 200
