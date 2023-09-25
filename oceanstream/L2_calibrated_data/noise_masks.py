"""
noise_masks.py
-------------------------
Description: Module for computing noise masks from Sv data.
"""
# import xarray as xr
from echopype.clean.api import (
    get_attenuation_mask_multichannel,
    get_impulse_noise_mask_multichannel,
    get_transient_noise_mask_multichannel,
)
from echopype.mask.api import get_seabed_mask_multichannel


def create_transient_mask(Sv, **kwargs):
    """
    Invokes echopype's get_transient_noise_mask_multichannel
    (see echopype's documentation for the possible parameters)

    Parameters:
        - Sv - the dataset we're trying to create a mask for
        - other arguments as required by the specific function used

    Returns:
        - a multichannel mask for transient noise

    Example:
        create_transient_mask(Sv)
    """
    mask = get_transient_noise_mask_multichannel(Sv, **kwargs)
    return mask


def create_impulse_mask(Sv, **kwargs):
    """
    Invokes echopype's get_impulse_noise_mask_multichannel
    (see echopype's documentation for the possible parameters)

    Parameters:
        - Sv - the dataset we're trying to create a mask for
        - other arguments as required by the specific function used

    Returns:
        - a multichannel mask for impulse noise

    Example:
        create_impulse_mask(Sv)
    """
    mask = get_impulse_noise_mask_multichannel(Sv, **kwargs)
    return mask


def create_attenuation_mask(Sv, **kwargs):
    """
    Invokes echopype's get_attenuation_mask_multichannel
    (see echopype's documentation for the possible parameters)

    Parameters:
        - Sv - the dataset we're trying to create a mask for
        - other arguments as required by the specific function used

    Returns:
        - a multichannel mask for attenuation noise

    Example:
        create_attenuation_mask(Sv)
    """
    mask = get_attenuation_mask_multichannel(Sv, **kwargs)
    return mask


def create_seabed_mask(Sv, **kwargs):
    """
    Invokes echopype's get_seabed_mask_multichannel
    (see echopype's documentation for the possible parameters)

    Parameters:
        - Sv - the dataset we're trying to create a mask for
        - other arguments as required by the specific function used

    Returns:
        - a multichannel mask for attenuation noise

    Example:
        create_seabed_mask(Sv)
    """
    mask = get_seabed_mask_multichannel(Sv, **kwargs)
    return mask


def add_metadata_to_mask(mask, metadata):
    """
    Brief description of the function.

    Parameters:
    - mask (xarray.Dataset): Mask to be attached
    - metadata (dict): Dictionary of metadata

    Returns:
    - xarray.Dataset - mask with metadata stored as global attributes

    Example:
    >>> add_metadata_to_mask(mask, metadata={"mask_type": "transient",
                                    "interpolation": "median_filtering"})
    Expected Output
    A mask with the metadata stored as global attributes
    """
    old_attrs = mask.attrs
    attrs = old_attrs.append(metadata)
    mask.attrs = attrs
    return mask


def attach_mask_to_dataset(Sv, mask, metadata):
    """
    Attaches a mask to an existing Sv dataset,
    so they can travel in one data structure to the next module

    Parameters:
    - Sv (xarray.Dataset): Dataset to attach a mask to
    - mask (xarray.Dataset): Mask to be attached
    - metadata (dict): Dictionary of metadata

    Returns:
    - xarray.Dataset - dataset enriched with the mask

    Example:
    >>> attach_mask_to_dataset(
        Sv,
        mask,
        metadata={"mask_type": "transient", "interpolation": "median_filtering"}
        )
    Expected Output

    """
    mask_with_metadata = add_metadata_to_mask(mask, metadata)
    return mask_with_metadata  # in progress
