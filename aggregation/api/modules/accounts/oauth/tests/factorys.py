import time
import uuid

import factory
from factory.alchemy import SQLAlchemyModelFactory
from werkzeug.security import gen_salt

from aggregation.api.modules.accounts.oauth.models import OAuth2Client, OAuth2Token
from aggregation import db
from aggregation.api.modules.accounts.tests.factory import UserFactory


class OAuth2ClientFactory(SQLAlchemyModelFactory):

    class Meta:
        model = OAuth2Client
        sqlalchemy_session = db.session

    client_name = "test"
    client_uri = "http://localhost:5000"
    scope = "basic"
    redirect_uri = client_uri
    grant_type = "authorization_code\npassword"
    response_type = "code"
    token_endpoint_auth_method = "client_secret_basic"
    client_id = gen_salt(24)
    client_secret = gen_salt(48)

    user = factory.SubFactory(UserFactory)


class OAuth2TokenFactory(SQLAlchemyModelFactory):

    class Meta:
        model = OAuth2Token
        sqlalchemy_session = db.session

    client_id = str(uuid.uuid4())[:24]
    token_type = "Bearer"
    issued_at = time.time()
    access_token = str(uuid.uuid4())[:48]
    scope = "Basic"
    expires_in = 3600 * 2
