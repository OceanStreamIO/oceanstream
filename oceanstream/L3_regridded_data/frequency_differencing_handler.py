"""
frequency_differencing_handler.py
---------------------------------
This module provides functionalities for species identification in echosounder data using
frequency differencing techniques.

Functions:

- `apply_freq_diff`:
It utilizes the `frequency_differencing` and `apply_mask` methods from the echopype library
to create and apply a mask based on the differences of Sv values using a pair of frequencies.

Usage:

To apply a frequency differencing mask to a given Sv dataset, `ds`, simply call:
`apply_freq_diff(ds, chanA, chanB, single_operator, single_value)`
or for interval-based masking:
`apply_freq_diffapply_freq_diff(ds,
                                chanA,
                                chanB,
                                interval_start_operator,
                                interval_start_value,
                                interval_end_operator,
                                interval_end_value,
                            )`

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
