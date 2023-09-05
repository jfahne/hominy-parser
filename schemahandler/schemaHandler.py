import io
import abc
from dataclasses import dataclass
from typing import Tuple, Any

import customfuncs
import errs
import header
import transformctx


@dataclass
class CreateCtx:
    Name: str
    Header: header.Header
    Content: io.bytearray
    CustomFuncs: customfuncs.CustomFuncs
    CreateParams: Any


class SchemaHandler(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (
            hasattr(subclass, "NewIngester")
            and callable(subclass.NewIngester)
            or NotImplemented
        )

    @abc.abstractmethod
    def NewIngester(
        input_ctx_mgr: io.TextIOBase, ctx: transformctx.Ctx = None
    ) -> Tuple["Ingester", Exception]:
        raise NotImplementedError


def CreateFunc(ctx: CreateCtx = None) -> Tuple[SchemaHandler, Exception]:
    pass


class RawRecord(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (
            hasattr(subclass, "Raw")
            and callable(subclass.Raw)
            and hasattr(subclass, "Checksum")
            and callable(subclass.Checksum)
            or NotImplemented
        )

    @abc.abstractmethod
    def Raw() -> Any:
        raise NotImplementedError

    @abc.abstractmethod
    def Checksum() -> str:
        raise NotImplementedError


class Ingester(errs.CtxAwareErr, metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        ctx_awr_err_schook = errs.CtxAwareErr.__subclasshook__(subclass)
        if ctx_awr_err_schook is NotImplemented:
            return NotImplemented
        elif not ctx_awr_err_schook:
            return False
        else:
            return (
                hasattr(subclass, "Read")
                and callable(subclass.Read)
                and hasattr(subclass, "IsContinuableError")
                and callable(subclass.IsContinuableError)
                or NotImplemented
            )

    @abc.abstractmethod
    def Read() -> Tuple[RawRecord, io.bytearray, Exception]:
        raise NotImplementedError

    @abc.abstractmethod
    def IsContinuableError(Exception) -> bool:
        raise NotImplementedError
