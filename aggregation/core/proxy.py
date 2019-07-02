from flask import request
from werkzeug.local import LocalProxy

current_action = LocalProxy(lambda: _get_current_action())


def _get_current_action():
    return request.action if hasattr(request, "action") else None


