import os
import time
import json
from functools import wraps

from flask.testing import FlaskClient
from flask_testing import TestCase
from sqlalchemy_utils import database_exists, create_database, drop_database

from aggregation import db
from aggregation import create_app
from aggregation.api.modules.accounts.oauth.models import OAuth2Token
from aggregation.api.modules.accounts.oauth.tests.factorys import OAuth2TokenFactory
from aggregation.settings import test_settings
from aggregation.api.modules.accounts.models import User


class CustomClient(FlaskClient):

    def open(self, *args, **kwargs):
        start = time.time()
        js = kwargs.pop('json', None)
        params = kwargs.pop("params", None)
        if js is not None:
            data = json.dumps(js)
            headers = kwargs.pop('headers', {})
            headers['Content-Type'] = 'application/json'
            kwargs['data'] = data
            kwargs['headers'] = headers

        user = kwargs.pop('user', None)
        if user is not None:
            assert isinstance(user, User)
            headers = kwargs.pop('headers', {})
            headers.update(self.get_user_authorization(user))
            kwargs['headers'] = headers
        target = args[0]
        if params is not None:
            assert isinstance(params, dict)
            url_params = ""
            for args_name, value in params.items():
                url_params += "{args_name}={value}&".format(args_name=args_name, value=value)
            url_params = url_params.strip("&")
            target += "?{url_params}".format(url_params=url_params)
            new_args = [target] + list(args)[1:]
            args = tuple(new_args)
        resp = super(CustomClient, self).open(*args, **kwargs)
        resp.target = target
        resp.elapsed = time.time() - start
        return resp

    @classmethod
    def get_user_authorization(cls, user):
        if user.oauth2_token:
            token = user.oauth2_token
        else:
            token = OAuth2TokenFactory(user=user)
            db.session.add(token)
            db.session.commit()
        return {"Authorization": 'Bearer %s' % token.access_token}


class AggregationTestCase(TestCase):
    TESTING: bool = True

    def create_app(self):
        app = create_app(test_settings)
        self.dsn = app.config.get("SQLALCHEMY_DATABASE_URI")
        if not database_exists(self.dsn):
            create_database(self.dsn)
        app.test_client_class = CustomClient
        return app

    def setUp(self) -> None:
        db.create_all()

    def tearDown(self) -> None:
        db.session.remove()
        db.drop_all()
        drop_database(self.dsn)


class AggregationAuthorizedTestCase(AggregationTestCase):

    def setUp(self):
        super(AggregationAuthorizedTestCase, self).setUp()
        from aggregation.api.modules.accounts.oauth.tests.factorys import OAuth2ClientFactory
        self.oauth_client = OAuth2ClientFactory()

        def decorator(f):
            @wraps(f)
            def wrapper(*args, **kwargs):
                if 'user' not in kwargs:
                    kwargs['user'] = self.oauth_client.user
                ret = f(*args, **kwargs)
                return ret

            return wrapper

        self.client.open = decorator(self.client.open)
