import uuid
import transformctx
from typing import Any, TypeAlias, Tuple
from collections.abc import Mapping
import time
from datetime import datetime, timezone

########################
# Port of datetime.go
########################

rfc3339NoTZ = "2006-01-02T15:04:05"
second = "SECOND"
millisecond = "MILLISECOND"
go_time_zero = time.struct_time((1, 1, 1, 0, 0, 0, 0, 1, 0))


def _ConvertTZ(t: time.struct_time, tz: str) -> time.struct_time:
    """
    Loose port of jf-tech/go-corelib/times::ConvertTZ
    ...
    Extended Summary
    ---
    There is not a simple way to replicate the times library from jf-tech/go-corelib
    with python builtins.
    Currently, the port will only support IANA time zone strings like "America/New_York".
    In future work, the shorthands offered by times.ConvertTZ() for offset to timezone mapping
    can be implemented.
    """
    dt_utc = datetime(*t[:6], tzinfo=timezone.utc)
    dt_tz = dt_utc.astimezone(fromTZ)
    return time.struct_time(
        tuple(
            a
            for a in [
                *dt_tz.timetuple(),
                ZoneInfo(tz),
                dt_tz.utcoffset().total_seconds(),
            ]
        )
    )

def _OverwriteTZ(t: time.struct_time, tz: str) -> time.struct_time:
    return time.struct_time(tuple(*t, ZoneInfo(tz), ZoneInfo(tz).utcoffset(datetime(*t[:6])).total_seconds()))


def parseDateTime(
    datetime: str, layout: str, layoutHasTZ: bool, fromTZ: str, toTZ: str
) -> Tuple[time.struct_time, bool, Exception]:
    if layout == "":
        try:
            t: time.struct_time = time.strptime(datetime)
            hasTZ = bool(t.tm_zone)
        except Exception as err:
            return go_time_zero, False, err
    else:
        try:
            t: time.struct_time = time.strptime(datetime, layout)
        except Exception as err:
            return go_time_zero, False, err
        hasTZ = layoutHasTZ
    if (not hasTZ) and (fromTZ != ""):
        try:
            t: time.struct_time = _ConvertTZ(t, toTZ)
        except Exception as err:
            return go_time_zero, False, err
    if toTZ != "":
        if hasTZ:
            try:
                t: time.struct_time = _ConvertTZ(t, toTZ)
            except Exception as err:
                return go_time_zero, False, err
        else:
            try:
                t: struct_time = _OverwriteTZ(t, toTZ)
                hasTZ = True
            except Exception as err:
                return go_time_zero, False, err
    return t, hasTZ, None


########################
# Port of customFuncs.go
########################

CustomFuncType: TypeAlias = Any
CustomFuncs: TypeAlias = Mapping[str, CustomFuncType]


def Merge(*funcs) -> CustomFuncs:
    merged = {name: f for name, f in funcs}
    return merged


def Coalesce(_: transformctx.Ctx = None, *strs) -> Tuple[string, Exception]:
    for _, s in strs:
        if s != "":
            return s, None
    return "", None


def Concat(_: transformctx.Ctx = None, *strs) -> Tuple[str, Exception]:
    result = "".join(strs)
    return result, None


def Lower(_: transform.Ctx, s: str = "") -> Tuple[str, Exception]:
    return s.lower(), None


def Upper(_: transformctx.Ctx = None, s: str = "") -> Tuple[str, Exception]:
    return s.upper(), None


def UUIDv3(_: transformctx.Ctx = None, s: str = "") -> Tuple[str, Exception]:
    return str(uuid.uuid3(uuid.UUID(int=0), s)), None


CommonCustomFuncs: Mapping[str, CustomFuncType] = {
    "coalesce": Coalesce,
    "concat": Concat,
    "dateTimeLayoutToRFC3339": DateTimeLayoutToRFC3339,
    "dateTimeToEpoch": DateTimeToEpoch,
    "dateTimeToRFC3339": DateTimeToRFC3339,
    "epochToDateTimeRFC3339": EpochToDateTimeRFC3339,
    "lower": Lower,
    "now": Now,
    "upper": Upper,
    "uuidv3": UUIDv3,
}
