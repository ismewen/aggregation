import base64
from aggregation import db
from aggregation.core.unnittest.testcase import AggregationTestCase


class OauthClientTest(AggregationTestCase):

    def test_some(self):
        from aggregation.api.modules.accounts.oauth.tests.factorys import OAuth2ClientFactory
        oauth2_client = OAuth2ClientFactory.build(grant_type="client_credentials")
        db.session.add(oauth2_client)
        db.session.commit()
        uri = "/oauth/token"
        auth_str = "%s:%s" % (oauth2_client.client_id, oauth2_client.client_secret)
        auth_token = base64.b64encode(bytes(auth_str, encoding="utf-8"))
        auth_token = str(auth_token, encoding='utf-8')
        headers = {
            "Authorization": "Basic %s" % auth_token
        }
        data = {
            "grant_type": "client_credentials",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        res = self.client.post(uri, data=data, headers=headers)

