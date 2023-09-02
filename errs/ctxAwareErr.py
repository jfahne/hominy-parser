class CtxAwareErr(Exception):
    def __init__(self, message_format, **kwargs):
        self._message = message_format.format(kwargs)
