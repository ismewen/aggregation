from aggregation.exceptions import HMTGeneralAPIError


class RequestError(HMTGeneralAPIError):
    code = 2001
    message = "%(message)s"


class AgentServerRequestError(RequestError):
    code = 2002
    message = "%s(message)s"
