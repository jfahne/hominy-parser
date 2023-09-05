import abc
from typing import Any


class CtxAwareErr(metaclass=abc.ABCMeta):
    """
    CtxAwareErr creates an error that is context aware.
    ...
    Extended Summary
    ---
    Examples of context aware error scenarios include:
    Schema parsing and validation:
    This interface can prefix errors with a schema name and line number.
    During input ingestion and trasforming:
    This interface can prefix errors with the input stream name and line number.
    """

    @classmethod
    def __subclasshook__(cls, subclass):
        return (
            hasattr(subclass, "FmtErr") and callable(subclass.FmtErr) or NotImplemented
        )

    @abc.abstractmethod
    def FmtError(self, format_in: str, *args: Any) -> Exception:
        raise NotImplementedError
