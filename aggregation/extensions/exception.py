from flask_babel import gettext as _


class HMTBaseException(Exception):
    """ 异常处理基类

        抛出异常::

            >>> HMTBaseException('Something wrong')
            HMTBaseException('Something wrong',)

        字典返回::
            >>> HMTBaseException('Something wrong').json_response()
            {'message': 'Something wrong', 'code': 1001}

        格式化字符串::
            >>> HMTBaseException('{name} wrong', format_kwargs={
            ... 'name': 'I am'}).json_response()
            {'message': 'I am wrong', 'code': 1001}

        响应返回::
            >>> HMTBaseException('wrong').api_response()[0].data

    :cvar code: 错误码
    :cvar status: Http响应码
    """
    code = 1001
    status = 400
    message = ''
    translate_format_keys = True

    def __init__(self, message=None, format_kwargs=None, *args, **kwargs):
        """

        :param message: 错误消息体
        :param format_kwargs: 消息格式化参数
        """
        if not format_kwargs:
            format_kwargs = dict()
        super(HMTBaseException, self).__init__(message, *args)

        if message is not None:
            self.message = message

        self._message = self.message
        self.message = self.message % format_kwargs

        self.format_params = format_kwargs

    def __str__(self):
        return self.message

    def __unicode__(self):
        return self.as_text()

    def json_response(self):
        return {
            'code': self.code,
            'message': self.as_text()
        }

    def as_text(self):
        if not self.format_params or not isinstance(self.format_params, dict):
            format_kwargs = {}
        else:
            if self.translate_format_keys:
                format_kwargs = dict((key, _(value)) for key, value in self.format_params.items())
            else:
                format_kwargs = self.format_params
        return _(self._message, **format_kwargs)
