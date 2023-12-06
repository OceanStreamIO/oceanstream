from typing import TypedDict, Optional, List, Union


class TransientParameters(TypedDict, total=False):
    m: int
    n: int
    thr: int
    excludeabove: int
    operation: str


class AttenuationParameters(TypedDict, total=False):
    r0: Optional[int]
    r1: Optional[int]
    n: int
    m: Optional[int]
    thr: int
    start: int
    offset: int


class ImpulseParameters(TypedDict, total=False):
    thr: int
    m: int
    n: int


class SeabedEchoParameters(TypedDict, total=False):
    theta: Optional[int]
    phi: Optional[int]
    r0: int
    r1: int
    tSv: int
    ttheta: int
    tphi: int
    wtheta: int
    wphi: int
    rlog: Optional[int]
    tpi: Optional[int]
    freq: Optional[int]
    rank: int


class SeabedParameters(TypedDict, total=False):
    r0: int
    r1: int
    roff: int
    thr: int
    ec: int
    ek: List[int]
    dc: int
    dk: List[int]


class MaskConfig(TypedDict):
    enabled: bool
    method: str
    parameters: Union[
        TransientParameters, AttenuationParameters, ImpulseParameters, SeabedEchoParameters, SeabedParameters]


class DenoiseConfig(TypedDict):
    transient: MaskConfig
    attenuation: MaskConfig
    impulse: MaskConfig
    seabed_echo: MaskConfig
    seabed: MaskConfig
    profile: bool
