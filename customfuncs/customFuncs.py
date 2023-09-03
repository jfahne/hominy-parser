import uuid
import transformctx
from typing import Any, TypeAlias, Tuple
from collections.abc import Mapping
import time
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

########################
# Port of datetime.go
########################

rfc3339NoTZ = "2006-01-02T15:04:05"
second = "SECOND"
millisecond = "MILLISECOND"
go_time_zero = time.struct_time((1, 1, 1, 0, 0, 0, 0, 1, 0))


def _ConvertTZ(t: time.struct_time, tz: str) -> time.struct_time:
    """Loose port of jf-tech/go-corelib/times::ConvertTZ"""
    dt_utc = datetime(*t[:6], tzinfo=timezone.utc)
    dt_tz = dt_utc.astimezone(ZoneInfo(tz))
    return time.struct_time(
        (*dt_tz.timetuple(), ZoneInfo(tz), dt_tz.utcoffset().total_seconds())
    )


def _OverwriteTZ(t: time.struct_time, tz: str) -> time.struct_time:
    return time.struct_time(
        (*t, ZoneInfo(tz), ZoneInfo(tz).utcoffset(datetime(*t[:6])).total_seconds())
    )


def parseDateTime(
    datetime_in: str, layout: str, layoutHasTZ: bool, fromTZ: str, toTZ: str
) -> Tuple[time.struct_time, bool, Exception]:
    if layout == "":
        try:
            t: time.struct_time = time.strptime(datetime_in)
            hasTZ = bool(t.tm_zone)
        except Exception as err:
            return go_time_zero, False, err
    else:
        try:
            t: time.struct_time = time.strptime(datetime_in, layout)
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
                t: time.struct_time = _OverwriteTZ(t, toTZ)
                hasTZ = True
            except Exception as err:
                return go_time_zero, False, err
    return t, hasTZ, None


def rfc3339(t: time.struct_time, hasTZ: bool) -> str:
    if hasTZ:
        return datetime(*t[:6], tzinfo=t.tm_zone).isoformat()
    return datetime(*t[:6]).isoformat()


def DateTimeToRFC3339(
    datetime_in: str, fromTZ: str, toTZ: str, _: transformctx.Ctx = None
) -> Tuple[str, Exception]:
    if datetime_in == "":
        return "", None
    t, hasTZ, err = parseDateTime(datetime_in, "", False, fromTZ, toTZ)
    if err is not None:
        return "", err
    return rfc3339(t, hasTZ), None


def _ParseBool(s: str) -> bool:
    truthy_vals = ["1", "t", "T", "TRUE", "true", "True"]
    falsy_vals = ["0", "f", "F", "FALSE", "false", "False"]
    if s in truthy_vals:
        return True
    elif s in falsy_vals:
        return False
    else:
        raise Exception(
            "Boolean value not parseable. " +
            "See https://pkg.go.dev/strconv#ParseBool for acceptable values."
        )


def DateTimeLayoutToRFC3339(
    datetime_in: str,
    layout: str,
    layoutTZ: str,
    fromTZ: str,
    toTZ: str,
    _: transformctx.Ctx = None,
) -> Tuple[str, Exception]:
    layoutTZFlag = False
    if (layout != "") and (layoutTZ != ""):
        try:
            layoutTZFlag = _ParseBool(layoutTZ)
        except Exception as err:
            return "", err
    if datetime_in == "":
        return "", None
    t, hasTZ, err = parseDateTime(datetime_in, layout, layoutTZFlag, fromTZ, toTZ)
    if err is not None:
        return "", None
    return rfc3339(t, hasTZ), None


epochUnitMilliseconds = "MILLISECOND"
epochUnitSeconds = "SECOND"


def DateTimeToEpoch(
    datetime_in: str, fromTZ: str, unit: str, _: transformctx.Ctx = None
) -> Tuple[str, Exception]:
    # NOTE: May have issues with python ints as source code uses 64 bit ints.
    if datetime_in == "":
        return "", None
    t, _, err = parseDateTime(datetime_in, "", False, fromTZ, "")
    if err is not None:
        return "", err
    if unit == epochUnitMilliseconds:
        return int(datetime(*t[:6], tzinfo=t.tm_zone).timestamp() * 1000), None
    elif epochUnitSeconds:
        return int(datetime(*t[:6], tzinfo=t.tm_zone).timestamp()), None
    else:
        return "", Exception(f"Unknown epoch unit {unit}.")


class _epoch_to_date_time_rfc3339_sentinel(str):
    pass


def EpochToDateTimeRFC3339(
    epoch: str,
    unit: str,
    tz: str = _epoch_to_date_time_rfc3339_sentinel(),
    _: transformctx.Ctx = None,
) -> Tuple[str, Exception]:
    if epoch == "":
        return "", None
    try:
        n = int(epoch)
    except Exception as err:
        return "", err
    tz_used = "UTC"
    if not isinstance(tz, _epoch_to_date_time_rfc3339_sentinel):
        tz_used = tz
    try:
        loc = ZoneInfo(tz_used)
    except Exception as err:
        return "", err
    if unit == epochUnitSeconds:
        dt = datetime.fromtimestamp(n).astimezone(loc)
        t = time.struct_time(
            (*dt.timetuple(), ZoneInfo(tz_used), dt.utcoffset().total_seconds())
        )
    elif unit == epochUnitMilliseconds:
        dt = datetime.fromtimestamp(n).astimezone(loc)
        t = time.struct_time(
            (*dt.timetuple(), ZoneInfo(tz_used), dt.utcoffset().total_seconds())
        )
    else:
        return "", Exception(f"Unknown epoch unit {unit}")
    return rfc3339(t, True), None


def Now(_: transformctx.Ctx = None) -> Tuple[str, Exception]:
    return rfc3339(time.struct_time((*time.gmtime(), ZoneInfo("UTC")), True)), None


########################
# Port of customFuncs.go
########################

CustomFuncType: TypeAlias = Any
CustomFuncs: TypeAlias = Mapping[str, CustomFuncType]


def Merge(*funcs) -> CustomFuncs:
    merged = {name: f for name, f in funcs}
    return merged


def Coalesce(*strs, _: transformctx.Ctx = None) -> Tuple[str, Exception]:
    for _, s in strs:
        if s != "":
            return s, None
    return "", None


def Concat(*strs, _: transformctx.Ctx = None) -> Tuple[str, Exception]:
    result = "".join(strs)
    return result, None


def Lower(s: str = "", _: transformctx.Ctx = None) -> Tuple[str, Exception]:
    return s.lower(), None


def Upper(s: str = "", _: transformctx.Ctx = None) -> Tuple[str, Exception]:
    return s.upper(), None


def UUIDv3(s: str = "", _: transformctx.Ctx = None) -> Tuple[str, Exception]:
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
