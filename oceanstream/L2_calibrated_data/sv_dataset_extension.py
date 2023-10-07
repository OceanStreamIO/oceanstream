"""
sv_dataset_extension.py
-----------------------

Module for enriching the volume backscattering strength (Sv) dataset by adding depth, location,
and split-beam angle information.

Functions:
- `enrich_sv_dataset`: Main function to enhance the Sv dataset by adding depth, location,
and split-beam angle information.

Usage:

To enrich an Sv dataset `sv` for a given EchoData object, `ed`, simply call:
`enriched_sv = enrich_sv_dataset(sv, ed, **kwargs)`

Note:
The specific keyword arguments (`**kwargs`) that can be passed to the function are dependent on
the `add_depth()`, `add_location()`, and `add_splitbeam_angle()` functions from the echopype module.
Refer to their respective documentation for details.

"""

import warnings

from echopype.consolidate import add_depth, add_location, add_splitbeam_angle
from echopype.echodata.echodata import EchoData
from xarray import Dataset


def enrich_sv_dataset(sv: Dataset, echodata: EchoData, **kwargs) -> Dataset:
    """
    Enhances the input `sv` dataset by adding depth, location, and split-beam angle information.

    Parameters:
    - sv (xr.Dataset): Volume backscattering strength (Sv) from the given echodata.
    - echodata (EchoData): An EchoData object holding the raw data.
    - **kwargs: Keyword arguments specific to `add_depth()`, `add_location()`, and `add_splitbeam_angle()`.
        Note: These functions are implemented in the echopype module.

    Returns:
    xr.Dataset:
        An enhanced dataset with depth, location, and split-beam angle.
    """
    # Extract keyword arguments specific to add_depth
    depth_keys = ["depth_offset", "tilt", "downward"]
    depth_args = {k: kwargs[k] for k in depth_keys if k in kwargs}
    # Extract keyword arguments specific to add_location
    location_keys = ["nmea_sentence"]
    location_args = {k: kwargs[k] for k in location_keys if k in kwargs}
    # Extract keyword arguments specific to add_splitbeam_angle
    splitbeam_keys = [
        "waveform_mode",
        "encode_mode",
        "pulse_compression",
        "storage_options",
        "return_dataset",
    ]
    splitbeam_args = {k: kwargs[k] for k in splitbeam_keys if k in kwargs}
    enriched_sv = sv.copy()
    # Add depth with error handling
    try:
        add_depth(enriched_sv, **depth_args)
    except Exception as e:
        warnings.warn(f"Failed to add depth due to error: {str(e)}")
    # Add location with error handling
    try:
        enriched_sv = add_location(enriched_sv, echodata, **location_args)
    except Exception as e:
        warnings.warn(f"Failed to add location due to error: {str(e)}")
    # Add split-beam angles with error handling
    try:
        add_splitbeam_angle(enriched_sv, echodata, **splitbeam_args)
    except Exception as e:
        warnings.warn(f"Failed to add split-beam angle due to error: {str(e)}")

    return enriched_sv
