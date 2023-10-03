"""
shoal_detection_handler.py
--------------------------
This module provides functionalities for shoal detection in echosounder data.

Functions:

- `create_shoal_mask_multichannel(ds, **kwargs)`:
    Generates two multichannel masks (`mask` and `mask_`) used for shoal detection based on the given Sv dataset.
- `combine_shoal_masks_multichannel(mask, mask_)`:
    Combines the multichannel masks (`mask` and `mask_`) to produce a final mask.
    The resulting mask contains `True` values only where both input masks are `True` for each channel.
- `apply_shoal_mask(ds, combined_masks)`:
    Applies a multichannel mask to the Sv data in the provided dataset.

Usage:

To create the two necessary multichannel shoal masks for a given Sv dataset, ds:
    >>> create_shoal_mask_multichannel(ds, **kwargs)
To combine two multichannel masks, `mask` and `mask_`:
    >>> combine_shoal_masks_multichannel(mask, mask_)
To apply the combined masks to a dataset, ds:
    >>> apply_shoal_mask(ds, combined_masks)

Notes:

- Ensure the echopype library is properly installed and imported when using this module.
- Sv represents the volume backscattering strength.
"""

from typing import Any, Tuple

import echopype as ep
import xarray as xr
from echopype.mask.api import get_shoal_mask_multichannel


def create_shoal_mask_multichannel(
    Sv: xr.Dataset, **kwargs: Any
) -> Tuple[xr.DataArray, xr.DataArray]:
    """
    Invokes echopype's `get_shoal_mask_multichannel` to create two multichannel masks used for shoal detection.

    Parameters:

    Sv : xr.Dataset
        The dataset for which the shoal masks will be created. This dataset should have the
        coordinate `channel` and variables `frequency_nominal` and `Sv`.

    **kwargs : Any
        Additional arguments required by the `get_shoal_mask_multichannel` function.
        Refer to echopype's documentation for the possible parameters.

    Returns:

    Tuple[xr.DataArray, xr.DataArray]
        A tuple containing two DataArrays:
        1. A multichannel mask (`mask`) for the Sv data. Regions that meet the thresholding criteria
           for shoal identification are marked as True.
        2. A mask (`mask_`) indicating the valid samples for the `mask`. Edge regions are filled
           with 'False', whereas the portion in which shoals could be detected is 'True'.

    Example:

    >>> mask, mask_ = create_shoal_mask_multichannel(Sv_dataset)
    """
    mask, mask_ = get_shoal_mask_multichannel(Sv, **kwargs)
    if "mask_type" in kwargs:
        mask_type_value = kwargs["mask_type"]
    else:
        mask_type_value = "will"
    mask.attrs["shoal detection mask type"] = mask_type_value
    mask_.attrs["shoal detection mask type"] = mask_type_value
    return mask, mask_


def combine_shoal_masks_multichannel(mask: xr.DataArray, mask_: xr.DataArray) -> xr.DataArray:
    """
    Combines the provided multichannel masks (`mask` and `mask_`) to produce a final mask that contains `True` values
    only where both input masks are `True` for each channel.

    Parameters:

    mask : xr.DataArray
        A multichannel mask for the Sv data. Regions satisfying the thresholding criteria
        for shoal identification are filled with `True`, else the regions are filled with `False`.

    mask_ : xr.DataArray
        A mask indicating the valid samples for the first mask. Edge regions are
        filled with 'False', whereas the portion in which shoals could be detected is 'True'.

    Returns:

    xr.DataArray
        A final multichannel mask for the Sv data. Regions that meet the thresholding criteria
        for shoal identification and fall within valid samples are marked as True.
        All other regions are marked as False.

    Example:

    >>> mask, mask_ = create_shoal_mask_multichannel(Sv_dataset)
    >>> combined_masks = combine_masks_multichannel(mask, mask_)
    """
    # Check if both masks have the 'channel' dimension
    if "channel" not in mask.dims or "channel" not in mask_.dims:
        raise ValueError("Both masks must have a 'channel' dimension for multichannel processing.")
    # Ensure the channels in both masks match
    if not all(mask["channel"].values == mask_["channel"].values):
        raise ValueError("Channels in both masks must match.")
    combined_masks = xr.where(mask & mask_, True, False)
    combined_masks.attrs["shoal detection mask type"] = mask.attrs["shoal detection mask type"]
    return combined_masks


def apply_shoal_mask(ds: xr.Dataset, combined_masks: xr.DataArray) -> xr.Dataset:
    """
    Apply a multichannel mask to the Sv data in the provided dataset.

    Parameters

    ds : xr.Dataset
        The dataset containing the Sv data to which the mask will be applied.
    combined_masks : xr.DataArray
        A final multichannel mask for the Sv data. Regions that meet the thresholding
        criteria for shoal identification and fall within valid samples are marked as True.
        All other regions are marked as False.

    Returns

    xr.Dataset
        A dataset with the applied mask.
    """
    return ep.mask.apply_mask(ds, combined_masks)
