import errs
from dataclasses import dataclass
from typing import Dict, Any, Tuple


@dataclass
class Ctx:
    InputName: str
    ExternalProperties: Dict[str, str]
    CtxAwareErr: errs.CtxAwareErr
    CustomParam: Any  # TODO: Typehint interface closer to golang

    def External(ctx: "Ctx", name: str) -> Tuple[str, bool]:
        v = ctx.ExternalProperties.get(name, default=None)
        return v, bool(v)
