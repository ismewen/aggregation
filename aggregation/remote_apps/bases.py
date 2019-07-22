import logging
from typing import Dict
from abc import ABCMeta, abstractmethod

import requests
from requests import Response

from aggregation import exceptions, settings
from aggregation.exceptions import HMTBaseException

logger = logging.getLogger("FileLogger")


class ClientBase(metaclass=ABCMeta):
    name: str = None
    host: str = None
    request_exception: type(HMTBaseException)

    def get_url(self, interface: str) -> str:
        return self.host + interface

    def get_headers(self, headers: Dict = None) -> Dict or None:
        return None

    @classmethod
    def get_auth(cls):
        return None

    @abstractmethod
    def handle_requests_res(self, res: Response) -> Response:
        pass

    def requests(self, interface, http_method: str = "GET", params: Dict = None, data: Dict = None, **kwargs):
        url = self.get_url(interface=interface)
        try:
            func = getattr(requests, http_method.lower())
            headers = kwargs.pop('headers', None)
            auth = kwargs.get('auth') or self.get_auth()
            res = func(url, params=params, data=data, headers=self.get_headers(headers), auth=auth, **kwargs)
        except Exception as e:
            print(params)
            print(data)
            debug_message = "interface: {interface}\n url: {url}\nhttp_method: {http_method}".format(
                interface=interface, url=url, http_method=http_method)
            logger.error(debug_message)
            raise exceptions.RequestError(format_kwargs=dict(message=str(e)))
        else:
            return self.handle_requests_res(res)

    def get_api(self, api_name):
        return RemoteAPIBase.api_registry.get(frozenset([self.name, api_name]))


class RemoteAPIBase(metaclass=ABCMeta):
    remote_app_name: str = None  # unique name
    name: str = None  # unique name
    interface_template: str = None  # str can use format
    api_registry: Dict = dict()  # all api

    def __init_subclass__(cls, **kwargs):
        registry_key = frozenset([cls.remote_app_name, cls.name])
        if not settings.TESTING:
            print(settings.TESTING)
            assert registry_key not in RemoteAPIBase.api_registry,\
                "%s in %s must be unique" % (cls.name, cls.remote_app_name)
        RemoteAPIBase.api_registry[registry_key] = cls

    def __init__(self, client: ClientBase):
        self.client = client
