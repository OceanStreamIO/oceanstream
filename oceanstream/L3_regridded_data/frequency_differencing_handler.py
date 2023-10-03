"""
frequency_differencing_handler.py
---------------------------------
This module provides functionalities for species identification in echosounder data using
frequency differencing techniques.

Functions:

- `apply_freq_diff`:
It utilizes the `frequency_differencing` and `apply_mask` methods from the echopype library
to create and apply a mask based on the differences of Sv values using a pair of frequencies.

- `identify_krill`:
A wrapper around `apply_freq_diff` tailored for krill identification based on
the difference in volume backscattering strength between 120 kHz and 38 kHz
typically ranging from 2 dB to 16 dB.

- `identify_gas_bearing_organisms`:
A wrapper around `apply_freq_diff` for identifying gas-bearing organisms using a specific
acoustic signature where the difference in volume backscattering strength between 120 kHz
and 38 kHz is less than -1 dB.

- `identify_fluid_like_organisms`:
A wrapper around `apply_freq_diff` for identifying fluid-like organisms using a specific
acoustic signature where the difference in volume backscattering strength between 120 kHz
and 38 kHz is greater than 2 dB.

Usage:

To apply a frequency differencing mask to a given Sv dataset, `ds`, simply call:
`apply_freq_diff(ds, chanA, chanB, single_operator, single_value)`
or for interval-based masking:
`apply_freq_diff(ds,
                 chanA,
                 chanB,
                 interval_start_operator,
                 interval_start_value,
                 interval_end_operator,
                 interval_end_value)`

For krill identification:
`identify_krill(ds, chan38, chan120)`

For gas-bearing organisms identification:
`identify_gas_bearing_organisms(ds, chan38, chan120)`

For fluid-like organisms identification:
`identify_fluid_like_organisms(ds, chan38, chan120)`

Note:
- Ensure that the echopype library is properly installed and imported when using this module.
- Sv = the volume backscattering strength

"""
from typing import Optional

import echopype as ep
import xarray as xr


def apply_freq_diff(
    ds: xr.Dataset,
    chanA: str,
    chanB: str,
    single_operator: Optional[str] = None,
    single_value: Optional[str] = None,
    interval_start_operator: Optional[str] = None,
    interval_start_value: Optional[str] = None,
    interval_end_operator: Optional[str] = None,
    interval_end_value: Optional[str] = None,
):
    """
    Create a mask based on the differences of Sv values using a pair of frequencies.
    This method is often referred to as the “frequency-differencing” or “dB-differencing” method.
    This function utilizes the `frequency_differencing` and `apply_mask` methods from the `echopype` library.

    Parameters:
    - ds (xr.Dataset): The dataset containing the Sv data to create a mask for.
    - chanA (str): Channel A name.
    - chanB (str): Channel B name.
    - single_operator (str, optional): Operator used for non-interval masking.
    - single_value (str, optional): Value used for non-interval masking.
    - interval_start_operator (str, optional): Operator defining the start of an interval.
    - interval_start_value (str, optional): Value defining the start of an interval.
    - interval_end_operator (str, optional): Operator defining the end of an interval.
    - interval_end_value (str, optional): Value defining the end of an interval.

    Returns:
    - xr.Dataset: A dataset with the applied mask.

    Notes:
    For more information about the `frequency_differencing` and `apply_mask` functions,
    refer to the echopype documentation.

    Raises:
    - ValueError: If an invalid combination of parameters is provided.
    """
    # If only single_operator and single_value are provided
    if single_operator is not None and single_value is not None:
        chanABEq_mask = f'"{chanA}" - "{chanB}" {single_operator} {single_value}dB'
        mask = ep.mask.frequency_differencing(source_Sv=ds, chanABEq=chanABEq_mask)
    # If interval parameters are provided
    elif (
        interval_start_operator is not None
        and interval_start_value is not None
        and interval_end_operator is not None
        and interval_end_value is not None
    ):
        chanABEq_low_mask = (
            f'"{chanA}" - "{chanB}" {interval_start_operator} {interval_start_value}dB'
        )
        chanABEq_high_mask = f'"{chanA}" - "{chanB}" {interval_end_operator} {interval_end_value}dB'
        low_mask = ep.mask.frequency_differencing(source_Sv=ds, chanABEq=chanABEq_low_mask)
        high_mask = ep.mask.frequency_differencing(source_Sv=ds, chanABEq=chanABEq_high_mask)
        mask = low_mask & high_mask
    else:
        raise ValueError("Invalid combination of parameters provided.")
    return ep.mask.apply_mask(ds, mask)


def identify_gas_bearing_organisms(ds: xr.Dataset, chan38: str, chan120: str) -> xr.Dataset:
    """
    Identify gas-bearing organisms using frequency differencing.
    Parameters:
    - ds (xr.Dataset): The dataset containing the Sv data to create a mask for.
    - chan38 (str): Channel name for 38 kHz.
    - chan120 (str): Channel name for 120 kHz.
    Returns:
    - xr.Dataset: A dataset with the applied mask for gas-bearing organisms identification.
    Notes:
    - Gas-bearing organisms are identified by an acoustic signature where the difference in volume
      backscattering strength between 120 kHz and 38 kHz is less than -1 dB.
    """
    return apply_freq_diff(
        ds=ds,
        chanA=chan38,
        chanB=chan120,
        single_operator=">",
        single_value="1",
    )


def identify_fluid_like_organisms(ds: xr.Dataset, chan38: str, chan120: str) -> xr.Dataset:
    """
    Identify fluid-like organisms using frequency differencing.
    Parameters:
    - ds (xr.Dataset): The dataset containing the Sv data to create a mask for.
    - chan38 (str): Channel name for 38 kHz.
    - chan120 (str): Channel name for 120 kHz.
    Returns:
    - xr.Dataset: A dataset with the applied mask for fluid-like organisms identification.
    Notes:
    Fluid-like organisms are identified by an acoustic signature where the difference in volume
    backscattering strength between 120 kHz and 38 kHz is greater than 2 dB.
    """
    return apply_freq_diff(
        ds=ds,
        chanA=chan120,
        chanB=chan38,
        single_operator=">",
        single_value="2.0",
    )


def identify_krill(ds: xr.Dataset, chan38: str, chan120: str) -> xr.Dataset:
    """
    Identify krill using frequency differencing intervals.
    Parameters:
    - ds (xr.Dataset): The dataset containing the Sv data to create a mask for.
    - chan38 (str): Channel name for 38 kHz.
    - chan120 (str): Channel name for 120 kHz.
    Returns:
    - xr.Dataset: A dataset with the applied mask for krill identification.
    Notes:
    The most prevalent frequency differencing interval for krill identification is given by:
    the difference in volume backscattering strength between 120 kHz and 38 kHz
    typically ranging from 2 dB to 16 dB.
    """
    return apply_freq_diff(
        ds=ds,
        chanA=chan120,
        chanB=chan38,
        interval_start_operator=">=",
        interval_start_value="2.0",
        interval_end_operator="<=",
        interval_end_value="16.0",
    )
