import logging

from authlib.oauth2 import OAuth2Error
from flask import Blueprint, render_template, session, redirect, abort
from flask import request
from flask_login import current_user
from werkzeug.security import gen_salt
from aggregation import db, exceptions
from aggregation.api.modules.accounts.models import User
from aggregation.api.modules.accounts.oauth.models import OAuth2Client
from aggregation.extensions.oauth import authorization

blueprint = Blueprint('oauth',
                      __name__,
                      template_folder='templates',
                      url_prefix='/oauth',
                      )

logger = logging.getLogger()



@blueprint.route('/', methods=('GET', 'POST'))
def home():
    if request.method == 'POST':
        username = request.form.get('username')
        user = User.query.filter_by(username=username).first()
        if not user:
            user = User(username=username)
            db.session.add(user)
            db.session.commit()
        session['id'] = user.id
        return redirect('/')
    user = current_user()
    if user:
        clients = OAuth2Client.query.filter_by(user_id=user.id).all()
    else:
        clients = []
    return render_template('home.html', user=user, clients=clients)


@blueprint.route('/login',methods=("GET", "POST"))
def login():
    email, password = request.values.get("email"), request.values.get("password")
    try:
        User.login(email=email, password=password)
        return "success", 200
    except exceptions.HMTGeneralAuthenticateError as e:
        return e.api_response()


@blueprint.route('/logout')
def logout():
    pass


@blueprint.route('/create_client', methods=('GET', 'POST'))
def create_client():
    user = current_user
    if not user:
        return redirect('/')
    if request.method == 'GET':
        return render_template('create_client.html')
    client = OAuth2Client(**request.form.to_dict(flat=True))
    client.user_id = user.id
    client.client_id = gen_salt(24)
    if client.token_endpoint_auth_method == 'none':
        client.client_secret = ''
    else:
        client.client_secret = gen_salt(48)
    db.session.add(client)
    db.session.commit()
    return redirect('/')


@blueprint.route('/authorize', methods=['GET', 'POST'])
def authorize():
    user = current_user
    import ipdb
    ipdb.set_trace()
    if request.method == 'GET':
        try:
            grant = authorization.validate_consent_request(end_user=user)
        except OAuth2Error as error:
            return error.error
        return render_template('authorize.html', user=user, grant=grant)
    if not user and 'username' in request.form:
        username = request.form.get('username')
        user = User.query.filter_by(username=username).first()
    if request.form['confirm']:
        grant_user = user
    else:
        grant_user = None
    return authorization.create_authorization_response(grant_user=grant_user)


@blueprint.route('/token', methods=['POST'])
def issue_token():
    if request.form.get("grant_type") == "password":
        User.login(**request.form)
    return authorization.create_token_response()


@blueprint.route('/revoke', methods=['POST'])
def revoke_token():
    return authorization.create_endpoint_response('revocation')
