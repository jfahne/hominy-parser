import io
from dataclasses import dataclass
from typing import Protocol
from collections.abc import Mapping


encodingUTF8 = "utf-8"
encodingISO8859_1 = "iso-8859-1"
encodingWindows1252 = "windows-1252"


class encodingMappingFunc(Protocol):
    def __call__(self, r: io.TextIOBase) -> io.TextIOBase:
        ...


def get_encodingUTF8(r: io.TextIOBase) -> io.TextIOBase:
    r.encoding = encodingUTF8
    return r


def get_encodingISO8859_1(r: io.TextIOBase) -> io.TextIOBase:
    r.encoding = encodingISO8859_1
    return r


def get_encodingWindows1252(r: io.TextIOBase) -> io.TextIOBase:
    r.encoding = encodingWindows1252
    return r


supportedEncodingMappings: Mapping[str, encodingMappingFunc] = {
    encodingUTF8: get_encodingUTF8,
    encodingISO8859_1: get_encodingISO8859_1,
    encodingWindows1252: get_encodingWindows1252,
}


@dataclass
class ParserSettings:
    Version: str
    FileFormatType: str
    Encoding: str = None

    def WrapEncoding(p: "ParserSettings", input_reader: io.TextIOBase):
        f = (
            supportedEncodingMappings[p.Encoding]
            if p.Encoding
            else supportedEncodingMappings[encodingUTF8]
        )
        return f(input_reader)


@dataclass
class Header:
    ParserSettings: ParserSettings
