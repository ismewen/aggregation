from .bases import HMTGeneralAPIError


class SqlalchemyCommitError(HMTGeneralAPIError):
    code = 1001
    message = "{error_message}"


class ObjectNotFoundError(HMTGeneralAPIError):
    code = 1002
    message = "Specific obj not found"


class SchemaValidationError(HMTGeneralAPIError):
    code = 1003
    message = 'Schema Validation Error'


class IllegalValueForField(HMTGeneralAPIError):
    code = 1004
    message = "Field {field}'s value is illegal"
