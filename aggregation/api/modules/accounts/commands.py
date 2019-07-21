from aggregation import db
from aggregation.api.modules.accounts.models import User


def add_user():
    user_name = input("please input user name:")
    password = input("please input password:")
    email = input("please input email")
    user = User(user_name=user_name, password=password, email=email)
    user.password = user.generate_password(user.password)
    db.session.add(user)
    db.session.commit()
    print("add user successfully")
    print("user_name: %s \n password: %s \n email: %s \n" % (user_name, password, email))


def create_oauth2_client():
    user_id = input("please input user id:")
    user = User.query.filter(User.id == user_id).first()
    if not user:
        raise Exception("user %s doesn't exists")
    client_name = input("please input oauth client name(default: test):")
    client_uri = input("please input client uri(default: http://localhost:5000):")
    scope = input("please input scope(default: basic):")
    redirect_uri = input("please input redirect uri(default: http://localhost:5000)")
    grant_type = input("please input grant type(default: authorization_code\npassword):")
    response_type = input("please input response type(default:code):")
    client_name = client_name or "test"
    client_uri = client_uri or "http://localhost:5000"
    scope = scope or "basic"
    redirect_uri = redirect_uri or "http://localhost:5000"
    grant_type = grant_type or "authorization_code\npassword"
    data = {
        "response_type": response_type,
        "client_name": client_name,
        "client_uri": client_uri,
        "scope": scope,
        "redirect_uri": redirect_uri,
        "grant_type": grant_type,
    }
    from aggregation.api.modules.accounts.oauth.tests.factorys import OAuth2ClientFactory
    oauth2_client = OAuth2ClientFactory.build(**data)
    oauth2_client.user = user
    db.session.add(oauth2_client)
    db.session.commit()
