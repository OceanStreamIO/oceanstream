"""
frequency_differencing_handler.py
---------------------------------
This module offers functionalities to identify species in echosounder data using frequency differencing techniques.

Functions:

- `find_mask_freq_diff`:
Generates a mask based on the differences in Sv values between two frequencies.
This method is commonly referred to as the “frequency-differencing” or “dB-differencing” method.
It leverages the `frequency_differencing` method from the `echopype` library.

- `attach_freq_diff_mask_to_ds`:
Attaches a frequency differencing mask to a given Sv DataArray.

- `identify_krill`:
Generates and attaches a mask tailored for krill identification.
Krill are typically identified by the difference in volume backscattering strength
between 120 kHz and 38 kHz, which ranges from 2 dB to 16 dB.

- `identify_gas_bearing_organisms`:
Generates and attaches a mask for identifying gas-bearing organisms.
These organisms exhibit an acoustic signature where the difference in volume backscattering strength
between 120 kHz and 38 kHz is less than -1 dB.

- `identify_fluid_like_organisms`:
Generates and attaches a mask for identifying fluid-like organisms.
These organisms are characterized by an acoustic signature
where the difference in volume backscattering strength between 120 kHz and 38 kHz is greater than 2 dB.

Usage:

To generate a frequency differencing mask for a given Sv DataArray, `ds`, use:
`find_mask_freq_diff(ds, chanA, chanB, single_operator, single_value)`
For interval-based masking, use:
`find_mask_freq_diff(ds, chanA, chanB, interval_start_operator, interval_start_value, interval_end_operator, interval_end_value)`

To identify and attach masks for specific organisms:
`identify_krill(ds, chan38, chan120)`
`identify_gas_bearing_organisms(ds, chan38, chan120)`
`identify_fluid_like_organisms(ds, chan38, chan120)`

Note:
- Ensure the echopype library is properly installed and imported when using this module.
- Sv represents the volume backscattering strength.

"""

from typing import Optional

import echopype as ep
import xarray as xr

from oceanstream.utils import add_metadata_to_mask, attach_mask_to_dataset


def find_mask_freq_diff(
    ds: xr.Dataset,
    chanA: str,
    chanB: str,
    single_operator: Optional[str] = None,
    single_value: Optional[str] = None,
    interval_start_operator: Optional[str] = None,
    interval_start_value: Optional[str] = None,
    interval_end_operator: Optional[str] = None,
    interval_end_value: Optional[str] = None,
) -> xr.DataArray:
    """
    Create a mask based on the differences of Sv values using a pair of frequencies.
    This method is often referred to as the “frequency-differencing” or “dB-differencing” method.
    This function utilizes the `frequency_differencing` method from the `echopype` library.

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
    - xr.DataArray: A DataArray containing the mask for the Sv data.

    Notes:
    For more information about the `frequency_differencing` function,
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
    return mask


def attach_freq_diff_mask_to_ds(Sv: xr.DataArray, mask: xr.DataArray) -> xr.DataArray:
    """
    Attach a frequency differencing mask to the given Sv DataArray.

    Parameters:
    - Sv (xr.DataArray): The DataArray containing the Sv data.
    - mask (xr.DataArray): The mask to be attached.

    Returns:
    - xr.DataArray: A DataArray with the attached mask.
    """
    return attach_mask_to_dataset(Sv, mask)


def identify_gas_bearing_organisms(ds: xr.Dataset, chan38: str, chan120: str) -> xr.Dataset:
    """
    Identify gas-bearing organisms using frequency differencing.
    Parameters:
    - ds (xr.Dataset): The dataset containing the Sv data to create a mask for.
    - chan38 (str): Channel name for 38 kHz.
    - chan120 (str): Channel name for 120 kHz.
    Returns:
    - xr.Dataset: A DataArray with the mask for gas-bearing organisms identification attached.
    Notes:
    - Gas-bearing organisms are identified by an acoustic signature where the difference in volume
      backscattering strength between 120 kHz and 38 kHz is less than -1 dB.
    """
    gas_bearing_mask = find_mask_freq_diff(
        ds=ds,
        chanA=chan38,
        chanB=chan120,
        single_operator=">",
        single_value="1",
    )
    gas_bearing_mask = add_metadata_to_mask(
        mask=gas_bearing_mask, metadata={"mask_type": "gas_bearing_organisms"}
    )

    return attach_freq_diff_mask_to_ds(ds, gas_bearing_mask)


def identify_fluid_like_organisms(ds: xr.Dataset, chan38: str, chan120: str) -> xr.Dataset:
    """
    Identify fluid-like organisms using frequency differencing.
    Parameters:
    - ds (xr.Dataset): The dataset containing the Sv data to create a mask for.
    - chan38 (str): Channel name for 38 kHz.
    - chan120 (str): Channel name for 120 kHz.
    Returns:
    - xr.Dataset: A DataArray with the mask for fluid-like organisms identification attached.
    Notes:
    Fluid-like organisms are identified by an acoustic signature where the difference in volume
    backscattering strength between 120 kHz and 38 kHz is greater than 2 dB.
    """
    fluid_like_mask = find_mask_freq_diff(
        ds=ds,
        chanA=chan120,
        chanB=chan38,
        single_operator=">",
        single_value="2.0",
    )
    fluid_like_mask = add_metadata_to_mask(
        mask=fluid_like_mask, metadata={"mask_type": "fluid_like_organisms"}
    )

    return attach_freq_diff_mask_to_ds(ds, fluid_like_mask)


def identify_krill(ds: xr.Dataset, chan38: str, chan120: str) -> xr.Dataset:
    """
    Identify krill using frequency differencing intervals.
    Parameters:
    - ds (xr.Dataset): The dataset containing the Sv data to create a mask for.
    - chan38 (str): Channel name for 38 kHz.
    - chan120 (str): Channel name for 120 kHz.
    Returns:
    - xr.Dataset: A DataArray with mask for krill identification attached.
    Notes:
    The most prevalent frequency differencing interval for krill identification is given by:
    the difference in volume backscattering strength between 120 kHz and 38 kHz
    typically ranging from 2 dB to 16 dB.
    """
    krill_mask = find_mask_freq_diff(
        ds=ds,
        chanA=chan120,
        chanB=chan38,
        interval_start_operator=">=",
        interval_start_value="2.0",
        interval_end_operator="<=",
        interval_end_value="16.0",
    )
    krill_mask = add_metadata_to_mask(mask=krill_mask, metadata={"mask_type": "krill"})

    return attach_freq_diff_mask_to_ds(ds, krill_mask)
