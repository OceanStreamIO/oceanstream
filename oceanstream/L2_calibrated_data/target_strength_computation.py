"""
target_strength_computation.py
-------------------------------

Module for computing the target strength (TS) from raw data.

Supported Sonar Models:
- EK60
- AZFP
- EK80

Functions and Classes:
- `SupportedSonarModelsForTS`: An Enum containing the sonar models supported
for TS computation.
- `WaveformMode`: Enum specifying the waveform mode ("CW" or "BB").
- `EncodeMode`: Enum indicating the encoding mode ("complex" or "power").
- `ComputeTSParams`: Class to validate and structure the parameters passed
to the TS computation function.
- `compute_target_strength`: Main function to calculate TS given an EchoData object
and other optional parameters. This function is based on the `echopype.calibrate.compute_TS()` function.

Usage:

To compute TS for a given EchoData object, `ed`, simply call:
`compute_target_strength(ed)`
"""

from enum import Enum
from typing import Any, Optional

import echopype as ep
import xarray as xr
from echopype.echodata.echodata import EchoData
from pydantic import BaseModel, ValidationError, field_validator


class SupportedSonarModelsForTS(str, Enum):
    EK60 = "EK60"
    AZFP = "AZFP"
    EK80 = "EK80"


class WaveformMode(str, Enum):
    CW = "CW"
    BB = "BB"


class EncodeMode(str, Enum):
    COMPLEX = "complex"
    POWER = "power"


class ComputeTSParams(BaseModel):
    echodata: Any
    env_params: Optional[dict] = None
    cal_params: Optional[dict] = None
    waveform_mode: Optional[WaveformMode] = None
    encode_mode: Optional[EncodeMode] = None

    @field_validator("echodata")
    def check_echodata_type(cls, value):
        if not isinstance(value, EchoData):
            raise ValueError("Invalid type for echodata. Expected an instance of EchoData.")
        return value


def compute_target_strength(echodata: EchoData, **kwargs) -> xr.Dataset:
    """
    Compute target strength (TS) from raw data.

    Parameters:
    - echodata (EchoData): The EchoData object containing
    sonar data for computation.
    - **kwargs: Additional keyword arguments passed to the TS computation.

    Returns:
    - xr.Dataset: A Dataset containing the computed TS values.

    Notes:
    This function:
    - Validates the `echodata`'s sonar model against supported models.
    - Uses the `ComputeTSParams` pydantic model to validate parameters.
    - Checks if the computed TS is empty.
    - Returns TS only if it is not empty.
    - Is based on the `echopype.calibrate.compute_TS()` function.

    """
    # Validate parameters using the pydantic model
    try:
        ComputeTSParams(echodata=echodata, **kwargs)
    except ValidationError as e:
        raise ValueError(str(e))
    # Check if the sonar model is supported
    sonar_model = echodata.sonar_model
    try:
        SupportedSonarModelsForTS(sonar_model)
    except ValueError:
        raise ValueError(
            f"Sonar model '{sonar_model}'\
                          is not supported for TS computation.\
                          Supported models are \
                            {list(SupportedSonarModelsForTS)}."
        )
    # Compute TS
    TS = ep.calibrate.compute_TS(echodata, **kwargs)
    # Check if the computed TS is empty
    if TS["TS"].values.size == 0:
        raise ValueError("Computed TS is empty!")
    return TS
