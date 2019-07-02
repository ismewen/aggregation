from flask import redirect, url_for, request, current_app
from flask_login import LoginManager

from aggregation.api.modules.accounts.models import User

login_manager = LoginManager()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)
