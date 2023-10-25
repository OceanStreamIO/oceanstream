from typing import Dict, List, Union

import numpy as np
import xarray


def dict_to_formatted_list(d: Dict[str, Union[int, str]]) -> List[str]:
    """Convert a dictionary to a list of formatted strings."""
    return [f"{key}={value}" for key, value in d.items()]


def add_metadata_to_mask(mask: xarray.Dataset, metadata: Dict) -> xarray.Dataset:
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


def attach_mask_to_dataset(Sv: xarray.Dataset, mask: xarray.Dataset) -> xarray.Dataset:
    """
    Attaches a mask to an existing Sv dataset, allowing the mask to travel in one data structure to the next module

    Parameters:
    - Sv (xarray.Dataset): dataset to attach a mask to
    - mask (xarray.Dataset): mask to be attached, with a mask_type attribute explaining what sort of mask it is

    Returns:
    - xarray.Dataset: dataset enriched with the mask

    Example:
        >>> attach_mask_to_dataset(Sv, mask)
    Expected Output:
        Sv with an extra variable containing the mask, named mask_[mask_type]
    """
    mask_type = mask.attrs["mask_type"]
    mask_name = "mask_" + mask_type
    Sv_mask = Sv.assign(mask=mask)
    Sv_mask["mask"].attrs = mask.attrs
    Sv_mask = Sv_mask.rename({"mask": mask_name})
    return Sv_mask


def attach_masks_to_dataset(Sv: xarray.Dataset, masks: [xarray.Dataset]) -> xarray.Dataset:
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


def haversine(type: str, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Given a pair of latitude/longitude points, calculate the great circle
    distance between them, in nautical miles
    Parameters:
    - type: string
        Type of distance unit to use (m, km, nm - nautical miles)
    - lat1: float
        Latitude of the first point
    - lon1: float
        Longitude of the first point
    - lat2: float
        Latitude of the second point
    - lon2: float
        Longitude of the second point

    Returns:
    - float: the distance in nautical miles
    """
    radius_dict = {"m": 6671008.8, "km": 6671.0088, "nm": 3440.065}
    if type not in radius_dict.keys():
        raise ValueError("Measuring unit not in available haversine units")
    earth_radius = radius_dict[type]
    lat1, lon1, lat2, lon2 = np.radians([lat1, lon2, lat2, lon2])

    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    c = 2 * np.arcsin(np.sqrt(a))
    distance = earth_radius * c
    return distance
