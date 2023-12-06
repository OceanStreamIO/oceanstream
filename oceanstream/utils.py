from typing import Dict, List, Union

import numpy as np
import xarray as xr


def dict_to_formatted_list(d: Dict[str, Union[int, str]]) -> List[str]:
    """Convert a dictionary to a list of formatted strings."""
    return [f"{key}={value}" for key, value in d.items()]


def add_metadata_to_mask(mask: xr.Dataset, metadata: Dict) -> xr.Dataset:
    """
    Attaches the provided metadata to the given mask as global attributes.

    Parameters:
    - mask (xarray.Dataset): mask to be attached
    - metadata (dict): dictionary of metadata

    Returns:
    - xarray.Dataset: mask with metadata stored as global attributes

    Example:
        >>> add_metadata_to_mask(mask, metadata={"mask_type": "transient",
                                    "interpolation": "median_filtering"})
    Expected Output:
    A mask with the metadata stored as global attributes
    """
    for k, v in metadata.items():
        mask.attrs[k] = v
    return mask


def attach_mask_to_dataset(Sv: xr.Dataset, mask: xr.Dataset, mask_type: str = None) -> xr.Dataset:
    """
    Attaches a mask to an existing Sv dataset, allowing the mask to travel in one data structure to the next module

    Parameters:
    - Sv (xarray.Dataset): dataset to attach a mask to
    - mask (xarray.Dataset): mask to be attached, with a mask_type attribute explaining what sort of mask it is
    - mask_type (str): type of mask to be attached (optional, if not specified, the mask_type attribute of the mask)

    Returns:
    - xarray.Dataset: dataset enriched with the mask

    Example:
        >>> attach_mask_to_dataset(Sv, mask)
    Expected Output:
        Sv with an extra variable containing the mask, named mask_[mask_type]
    """
    if mask_type is None:
        mask_type = mask.attrs["mask_type"]

    mask_name = "mask_" + mask_type
    Sv_mask = Sv.assign(mask=mask)
    Sv_mask["mask"].attrs = mask.attrs
    Sv_mask = Sv_mask.rename({"mask": mask_name})

    return Sv_mask


def attach_masks_to_dataset(Sv: xr.Dataset, masks: [xr.Dataset]) -> xr.Dataset:
    """
    Attaches masks to an existing Sv dataset,
    so they can travel in one data structure to the next module

    Parameters:
    - Sv (xarray.Dataset): dataset to attach the masks to
    - masks (xarray.Dataset[]): masks to be attached

    Returns:
    - xarray.Dataset: dataset enriched with the masks as separate variables

    Example:
        >>> attach_masks_to_dataset(Sv, masks)
    Expected Output:
    - Sv with extra variables containing the masks, named mask_[mask_type]
    """
    for mask in masks:
        Sv = attach_mask_to_dataset(Sv, mask)
    return Sv


def tfc(mask: xr.DataArray):
    """
    Counts true and false values in a xarray (usually a mask)

    Parameters:
    - mask (xarray.DataArray): boolean xarray

    Returns:
    - (): tuple where the first value is the count of true values
    and the second one is the count of false values

    Example:
        >>> tfc(mask)
    """
    count_true = np.count_nonzero(mask)
    count_false = mask.size - count_true
    true_false_counts = (count_true, count_false)
    return true_false_counts


