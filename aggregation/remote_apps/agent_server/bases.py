from typing import Dict

from requests import Response

from aggregation import settings, exceptions
from aggregation.api.modules.cluster.models import Cluster
from aggregation.remote_apps.bases import ClientBase, RemoteAPIBase


class AgentServerClient(ClientBase):
    name = "agent_server"  # unique name

    def __init__(self, cluster: Cluster):
        self.cluster = cluster
        self.host = cluster.get_host()

    def get_headers(self, headers: Dict = None) -> Dict:
        default_headers = {
            "Content-Type": "Application/json"
        }
        headers = headers or dict()
        default_headers.update(headers)
        return default_headers

    def get_auth(self):
        user = settings.AGENT_SERVER_USER
        password = settings.AGENT_SERVER_PASSWORD
        return user, password

    def handle_requests_res(self, res: Response) -> Response:
        if not str(res.status_code).startswith("2"):
            message = None
            try:
                message = res.json().get("error")
            except Exception as e:
                pass
            if not message:
                print(res)
                logger.info("error info: %s" % res.text)
                message = "requests {}  failed, response code: {}".format(res.url, res.status_code)
            raise exceptions.AgentServerRequestError(message)
        return res

    def __getattr__(self, item):
        message = "AttributeError: '%s' object has no attribute '%s'" % (self.__class__.__name__, item)
        if item.startswith("api_"):
            api_name = item.split("_")[1]
            key = frozenset([self.name, api_name])
            api_cls = RemoteAPIBase.api_registry.get(key)
            if api_cls:
                value = api_cls(self)
                self.__dict__[item] = value
                return value
            else:
                raise AttributeError(message)
        else:
            raise AttributeError(message)


class AgentServerAPI(RemoteAPIBase):
    name = "agent_server"
    remote_app_name = "agent_server"

