"""
compute_sv.py
-------------

Module for computing the volume backscattering strength (Sv) from raw data.
Supported Sonar Models:
- EK60
- AZFP
- EK80
Functions and Classes:
- `SupportedSonarModelsForSv`: An Enum containing the sonar models supported
for Sv computation.
- `WaveformMode`: Enum specifying the waveform mode (CW or BB).
- `EncodeMode`: Enum indicating the encoding mode (complex or power).
- `ComputeSVParams`: Class to validate and structure the parameters passed
to the Sv computation function.
- `compute_sv`: Main function to calculate Sv given an EchoData object
and other optional parameters.

Usage:

To compute Sv for a given EchoData object, `ed`, simply call:
`compute_sv(ed)`
"""

from enum import Enum
from typing import Any, Optional

import echopype as ep
import xarray as xr
from echopype.echodata.echodata import EchoData
from pydantic import BaseModel, ValidationError, field_validator
from pydantic_core.core_schema import FieldValidationInfo


class SupportedSonarModelsForSv(str, Enum):
    EK60 = "EK60"
    AZFP = "AZFP"
    EK80 = "EK80"


class WaveformMode(str, Enum):
    CW = "CW"
    BB = "BB"


class EncodeMode(str, Enum):
    COMPLEX = "complex"
    POWER = "power"


class ComputeSVParams(BaseModel):
    echodata: Any
    env_params: Optional[dict] = None
    cal_params: Optional[dict] = None
    waveform_mode: Optional[WaveformMode] = None
    encode_mode: Optional[EncodeMode] = None

    @field_validator("echodata")
    def check_echodata_type(cls, value):
        if not isinstance(value, EchoData):
            raise ValueError(
                "Invalid type for echodata. Expected an instance of EchoData."
            )
        return value

    @field_validator("waveform_mode")
    def check_waveform_mode(cls, waveform_mode, info: FieldValidationInfo):
        echodata = info.data.get("echodata")
        is_not_ek80 = echodata and echodata.sonar_model != "EK80"
        if is_not_ek80 and waveform_mode is not None:
            raise ValueError(
                f"waveform_mode is only valid for EK80. \
                    Got sonar_model='{echodata.sonar_model}'"
            )
        return waveform_mode

    @field_validator("encode_mode")
    def check_encode_mode(cls, encode_mode, info: FieldValidationInfo):
        echodata = info.data.get("echodata")
        is_not_ek80 = echodata and echodata.sonar_model != "EK80"
        if is_not_ek80 and encode_mode is not None:
            raise ValueError(
                f"encode_mode is only valid for EK80. \
                    Got sonar_model='{echodata.sonar_model}'"
            )
        return encode_mode


def compute_sv(echodata: EchoData, **kwargs) -> xr.Dataset:
    """
    Computes the volume backscattering strength (Sv) from the given echodata.

    Parameters:
    - echodata (EchoData): The EchoData object containing
    sonar data for computation.
    - **kwargs: Additional keyword arguments passed to the Sv computation.

    Returns:
    - xr.Dataset: A Dataset containing the computed Sv values.

    Example:
    >>> sv_results = compute_sv(echodata_object)
    >>> print(sv_results)

    Notes:
    This function:
    - Validates the `echodata`'s sonar model against supported models.
    - Uses the `ComputeSVParams` pydantic model to validate parameters.
    - Checks if the computed Sv is empty.
    - Returns Sv only if it is not empty.

    """
    sonar_model = echodata.sonar_model
    # Check if the sonar model is supported
    try:
        SupportedSonarModelsForSv(sonar_model)
    except ValueError:
        raise ValueError(
            f"Sonar model '{sonar_model}'\
                          is not supported for Sv computation.\
                          Supported models are \
                            {list(SupportedSonarModelsForSv)}."
        )

    # Validate parameters using the pydantic model
    try:
        ComputeSVParams(echodata=echodata, **kwargs)
    except ValidationError as e:
        raise ValueError(str(e))
    # Compute Sv
    Sv = ep.calibrate.compute_Sv(echodata, **kwargs)
    # Check if the computed Sv is empty
    if Sv["Sv"].values.size == 0:
        raise ValueError("Computed Sv is empty!")
    return Sv
