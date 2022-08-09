from flask import request
from werkzeug.local import LocalProxy

current_action = LocalProxy(lambda: _get_current_action())
mandatory_params = LocalProxy(lambda: _get_mandatory_params())


def _get_current_action():
    return request.action if hasattr(request, "action") else dict()


def _get_mandatory_params():
    return request.mandatory_params if hasattr(request, "mandatory_params") else dict()
