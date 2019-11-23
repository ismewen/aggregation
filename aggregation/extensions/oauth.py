from authlib.oauth2.rfc6749 import *

from aggregation import db
from authlib.flask.oauth2 import AuthorizationServer, ResourceProtector
from authlib.flask.oauth2.sqla import (
    create_query_client_func,
    create_save_token_func,
    create_revocation_endpoint,
    create_bearer_token_validator,
)
from authlib.specs.rfc6749 import grants
from werkzeug.security import gen_salt

from aggregation.api.modules.accounts.models import User
from aggregation.api.modules.accounts.oauth.models import OAuth2AuthorizationCode, OAuth2Token, OAuth2Client


class AuthorizationCodeGrant(grants.AuthorizationCodeGrant):
    def create_authorization_code(self, client, user, request):
        code = gen_salt(48)
        item = OAuth2AuthorizationCode(
            code=code,
            client_id=client.client_id,
            redirect_uri=request.redirect_uri,
            scope=request.scope,
            user_id=user.id,
        )
        db.session.add(item)
        db.session.commit()
        return code

    def parse_authorization_code(self, code, client):
        item = OAuth2AuthorizationCode.query.filter_by(
            code=code, client_id=client.client_id).first()
        if item and not item.is_expired():
            return item

    def delete_authorization_code(self, authorization_code):
        db.session.delete(authorization_code)
        db.session.commit()

    def authenticate_user(self, authorization_code):
        return User.query.get(authorization_code.user_id)


class PasswordGrant(grants.ResourceOwnerPasswordCredentialsGrant):


    def validate_token_request(self):
        """The client makes a request to the token endpoint by adding the
        following parameters using the "application/x-www-form-urlencoded"
        format per Appendix B with a character encoding of UTF-8 in the HTTP
        request entity-body:

        grant_type
             REQUIRED.  Value MUST be set to "password".

        username
             REQUIRED.  The resource owner username.

        password
             REQUIRED.  The resource owner password.

        scope
             OPTIONAL.  The scope of the access request as described by
             Section 3.3.

        If the client type is confidential or the client was issued client
        credentials (or assigned other authentication requirements), the
        client MUST authenticate with the authorization server as described
        in Section 3.2.1.

        For example, the client makes the following HTTP request using
        transport-layer security (with extra line breaks for display purposes
        only):

        .. code-block:: http

            POST /token HTTP/1.1
            Host: server.example.com
            Authorization: Basic czZCaGRSa3F0MzpnWDFmQmF0M2JW
            Content-Type: application/x-www-form-urlencoded

            grant_type=password&username=johndoe&password=A3ddj3w
        """
        # ignore validate for grant_type, since it is validated by
        # check_token_endpoint
        client = self.authenticate_token_endpoint_client()

        if not client.check_grant_type(self.GRANT_TYPE):
            raise UnauthorizedClientError()

        params = self.request.data
        if 'email' not in params:
            raise InvalidRequestError('Missing "email" in request.')
        if 'password' not in params:
            raise InvalidRequestError('Missing "password" in request.')

        user = self.authenticate_user(
            params['email'],
            params['password']
        )
        if not user:
            raise InvalidGrantError(
                'Invalid "username" or "password" in request.',
            )
        self.validate_requested_scope(client)
        self.request.client = client
        self.request.user = user

    def authenticate_user(self, email, password):
        user = User.query.filter_by(email=email).first()
        if user.check_password(password):
            return user


class RefreshTokenGrant(grants.RefreshTokenGrant):
    def authenticate_refresh_token(self, refresh_token):
        item = OAuth2Token.query.filter_by(refresh_token=refresh_token).first()
        if item and not item.is_refresh_token_expired():
            return item

    def authenticate_user(self, credential):
        return User.query.get(credential.user_id)


query_client = create_query_client_func(db.session, OAuth2Client)
save_token = create_save_token_func(db.session, OAuth2Token)

authorization = AuthorizationServer(
    query_client=query_client,
    save_token=save_token,
)

require_oauth = ResourceProtector()

bearer_cls = create_bearer_token_validator(db.session, OAuth2Token)
require_oauth.register_token_validator(bearer_cls())


def config_oauth(app):
    authorization.init_app(app)

    # support all grants
    authorization.register_grant(grants.ImplicitGrant)
    authorization.register_grant(grants.ClientCredentialsGrant)
    authorization.register_grant(AuthorizationCodeGrant)
    authorization.register_grant(PasswordGrant)
    authorization.register_grant(RefreshTokenGrant)

    # support revocation
    revocation_cls = create_revocation_endpoint(db.session, OAuth2Token)
    authorization.register_endpoint(revocation_cls)

    # protect resource
    bearer_cls = create_bearer_token_validator(db.session, OAuth2Token)
    require_oauth.register_token_validator(bearer_cls())
