class ErrSchemaNotSupported(Exception):
    "ErrSchemaNotSupported indicates a schema is not supported by a handler."

    @staticmethod
    def __init__():
        super().__init__("schema not supported")


class ErrTransformFailed(Exception):
    pass


def IsErrTransformFailed(err: Exception) -> bool:
    return isinstance(err, ErrTransformFailed)
