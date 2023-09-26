"""
noise_masks.py
-------------------------
Description: Module for computing noise masks from Sv data.
"""
import xarray

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
    for k, v in metadata.items():
        mask.attrs[k] = v
    return mask


def attach_mask_to_dataset(Sv: xarray.Dataset, mask: xarray.Dataset):
    """
    Attaches a mask to an existing Sv dataset,
    so they can travel in one data structure to the next module

    Parameters:
    - Sv (xarray.Dataset): Dataset to attach a mask to
    - mask (xarray.Dataset): Mask to be attached, with a mask_type attribute
        explaining what sort of mask it is

    Returns:
    - xarray.Dataset - dataset enriched with the mask

    Example:
    >>> attach_mask_to_dataset(Sv, mask)
    Expected Output
        Sv with an extra variable containing the mask, named mask_[mask_type]
    """
    print(mask)
    print(mask.attrs)
    mask_type = mask.attrs["mask_type"]
    mask_name = "mask_" + mask_type
    Sv_mask = Sv.assign(mask=mask)
    Sv_mask["mask"].attrs = mask.attrs
    Sv_mask = Sv_mask.rename({"mask": mask_name})
    return Sv_mask


def attach_masks_to_dataset(Sv: xarray.Dataset, masks: [xarray.Dataset]):
    """
    Attaches a mask to an existing Sv dataset,
    so they can travel in one data structure to the next module

    Parameters:
    - Sv (xarray.Dataset): Dataset to attach a mask to
    - masks (xarray.Dataset[]): Masks to be attached

    Returns:
    - xarray.Dataset - dataset enriched with the masks as separate variables

    Example:
    >>> attach_mask_to_dataset(Sv, masks)
    Expected Output
        Sv with extra variables containing the masks, named mask_[mask_type]
    """
    for mask in masks:
        Sv = attach_mask_to_dataset(Sv, mask)
    return Sv


def create_noise_masks_rapidkrill(source_Sv: xarray.Dataset):
    """
    A function that creates noise masks for a given Sv dataset according to
    rapidkrill processing needs

    Parameters:
    - Sv (xarray.Dataset): Dataset to attach a mask to
    - arg2 (type): Description of arg2.

    Returns:
    - xarray.Dataset: a dataset with the same dimensions as the original,
    containing the original data and four masks: mask_transient, mask_impulse,
    mask_attenuated, mask_seabed

    Example:
    >>> function_name_1(value1, value2)
    Expected Output
    a dataset with the same dimensions as the original, containing the original
    data and four masks: mask_transient, mask_impulse, mask_attenuation, mask_seabed
    """
    transient_mask = create_transient_mask(source_Sv, method="ryan", n=20, thr=20, excludeabove=250)
    transient_mask = add_metadata_to_mask(mask=transient_mask, metadata={"mask_type": "transient"})
    attenuation_mask = create_attenuation_mask(
        source_Sv, method="ryan", r0=180, r1=280, n=30, m=None, thr=-6, start=0, offset=0
    )
    attenuation_mask = add_metadata_to_mask(
        mask=attenuation_mask, metadata={"mask_type": "attenuation"}
    )
    impulse_mask = create_impulse_mask(
        source_Sv, method="wang", thr=(-70, -40), erode=[(3, 3)], dilate=[(7, 7)], median=[(7, 7)]
    )
    impulse_mask = add_metadata_to_mask(mask=impulse_mask, metadata={"mask_type": "impulse"})
    seabed_mask = create_seabed_mask(
        source_Sv,
        method="ariza",
        r0=20,
        r1=1000,
        roff=0,
        thr=-38,
        ec=1,
        ek=(3, 3),
        dc=10,
        dk=(3, 7),
    )
    seabed_mask = add_metadata_to_mask(mask=seabed_mask, metadata={"mask_type": "seabed"})
    seabed_echo_mask = create_seabed_mask(
        source_Sv,
        method="blackwell",
    )
    seabed_echo_mask = add_metadata_to_mask(
        mask=seabed_echo_mask, metadata={"mask_type": "false_seabed"}
    )
    masks = [transient_mask, impulse_mask, attenuation_mask, seabed_mask, seabed_echo_mask]
    Sv_mask = attach_masks_to_dataset(source_Sv, masks)
    return Sv_mask
