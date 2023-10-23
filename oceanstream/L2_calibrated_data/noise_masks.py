"""
noise_masks.py
---------------
Description: Module for computing noise masks from Sv data.
"""


import pathlib
from typing import Union

import xarray
import xarray as xr
from echopype.clean.api import (
    get_attenuation_mask_multichannel,
    get_impulse_noise_mask_multichannel,
    get_transient_noise_mask_multichannel,
)
from echopype.mask.api import get_seabed_mask_multichannel

from oceanstream.utils import add_metadata_to_mask, attach_masks_to_dataset, dict_to_formatted_list


def create_transient_mask(
    Sv: Union[xr.Dataset, str, pathlib.Path], parameters: dict, method: str = "ryan"
):
    """
    Invokes echopype's get_transient_noise_mask_multichannel
    (see echopype's documentation)

    Parameters:
    - Sv: xr.Dataset or str or pathlib.Path
        If a Dataset this value contains the Sv data to create a mask for,
        else it specifies the path to a zarr or netcdf file containing
        a Dataset. This input must correspond to a Dataset that has the
        coordinate ``channel`` and variables ``frequency_nominal`` and ``Sv``.
    - method: str with either "ryan" or "fielding" based on
        the preferred method for transient noise mask generation
    - parameters: dict
        Default method parameters

    Returns:
    - A multichannel mask for transient noise

    Example:
        >>> create_transient_mask(Sv, parameters, method)
    """
    mask = get_transient_noise_mask_multichannel(Sv, parameters, method)
    return mask


def create_impulse_mask(
    Sv: xr.Dataset,
    parameters: dict,
    method: str = "ryan",
) -> xr.DataArray:
    """
    Invokes echopype's get_impulse_noise_mask_multichannel
    (see echopype's documentation)

    Parameters:
    - Sv: xr.Dataset
        Dataset  containing the Sv data to create a mask for
    - method: str, optional
        The method (ryan, ryan iterable or wang) used to mask impulse noise. Defaults to 'ryan'.
    - parameters: dict
        Default method parameters

    Returns:
    - A multichannel mask for impulse noise

    Example:
        >>> create_impulse_mask(Sv, parameters, method)
    """
    mask = get_impulse_noise_mask_multichannel(Sv, parameters, method)
    return mask


def create_attenuation_mask(
    Sv: Union[xr.Dataset, str, pathlib.Path],
    parameters: dict,
    method: str = "ryan",
) -> xr.DataArray:
    """
    Invokes echopype's get_attenuation_mask_multichannel
    (see echopype's documentation)

    Parameters:
    - Sv: xr.Dataset or str or pathlib.Path
        If a Dataset this value contains the Sv data to create a mask for,
        else it specifies the path to a zarr or netcdf file containing
        a Dataset. This input must correspond to a Dataset that has the
        coordinate ``channel`` and variables ``frequency_nominal`` and ``Sv``.
    - method: str with either "ryan" or "ariza" based on the
        preferred method for signal attenuation mask generation
    - parameters: dict
        Default method parameters

    Returns:
    - A multichannel mask for attenuation noise

    Example:
        >>> create_attenuation_mask(Sv, parameters, method)
    """
    mask = get_attenuation_mask_multichannel(Sv, parameters, method)
    return mask


def create_seabed_mask(Sv, parameters, method):
    """
    Invokes echopype's get_seabed_mask_multichannel
    (see echopype's documentation for the possible parameters)

    Parameters:
    - Sv: the dataset we're trying to create a mask for
    - method: str with either "ariza", "experimental", "blackwell_mod",
    "blackwell", "deltaSv", "maxSv" based on the preferred method for seabed mask generation
    - parameters: dict
        Default method parameters

    Returns:
    - Multichannel mask for seabed detection

    Example:
        >>> create_seabed_mask(Sv, parameters, method)
    """
    mask = get_seabed_mask_multichannel(Sv, parameters, method)
    return mask


def create_noise_masks_rapidkrill(source_Sv: xarray.Dataset):
    """
    A function that creates noise masks for a given Sv dataset according to
    rapidkrill processing needs

    Parameters:
    - source_Sv (xarray.Dataset): the dataset to which the masks will be attached.

    Returns:
    - xarray.Dataset: a dataset with the same dimensions as the original,
    containing the original data and five masks: mask_transient, mask_impulse,
    mask_attenuated, mask_seabed, mask_false_seabed

    Notes:
    - To effectively utilize the `blackwell` method for seabed detection,
    it's essential that the `source_Sv` dataset includes the `split-beam angle` parameters.
    Specifically, ensure that your input `source_Sv` contains
    both the `angle_alongship` and `angle_athwartship` variables.
    Absence of these variables leads to errors .
    """
    rapidkrill_transient_mask_params = {
        "m": 5,
        "n": 20,
        "thr": 20,
        "excludeabove": 250,
        "operation": "percentile15",
    }
    transient_mask = create_transient_mask(
        source_Sv, parameters=rapidkrill_transient_mask_params, method="ryan"
    )
    transient_mask = add_metadata_to_mask(
        mask=transient_mask,
        metadata={
            "mask_type": "transient",
            "method": "ryan",
            "parameters": dict_to_formatted_list(rapidkrill_transient_mask_params),
        },
    )

    rapidkrill_attenuation_mask_params = {
        "r0": 180,
        "r1": 280,
        "n": 30,
        "m": None,
        "thr": -6,
        "start": 0,
        "offset": 0,
    }
    attenuation_mask = create_attenuation_mask(
        source_Sv, parameters=rapidkrill_attenuation_mask_params, method="ryan"
    )
    attenuation_mask = add_metadata_to_mask(
        mask=attenuation_mask,
        metadata={
            "mask_type": "attenuation",
            "method": "ryan",
            "parameters": dict_to_formatted_list(rapidkrill_attenuation_mask_params),
        },
    )

    rapidkrill_impulse_mask_param = {"thr": 10, "m": 5, "n": 1}
    impulse_mask = create_impulse_mask(
        source_Sv, parameters=rapidkrill_impulse_mask_param, method="ryan"
    )
    impulse_mask = add_metadata_to_mask(
        mask=impulse_mask,
        metadata={
            "mask_type": "impulse",
            "method": "ryan",
            "parameters": dict_to_formatted_list(rapidkrill_impulse_mask_param),
        },
    )

    rapidkrill_seabed_mask_params = {
        "r0": 10,
        "r1": 1000,
        "roff": 0,
        "thr": -40,
        "ec": 1,
        "ek": (1, 3),
        "dc": 10,
        "dk": (3, 7),
    }
    seabed_mask = create_seabed_mask(
        source_Sv,
        method="ariza",
        parameters=rapidkrill_seabed_mask_params,
    )
    seabed_mask = add_metadata_to_mask(
        mask=seabed_mask,
        metadata={
            "mask_type": "seabed",
            "method": "ariza",
            "parameters": dict_to_formatted_list(rapidkrill_seabed_mask_params),
        },
    )

    rapidkrill_seabed_echo_mask_params = {
        "theta": None,
        "phi": None,
        "r0": 10,
        "r1": 1000,
        "tSv": -75,
        "ttheta": 702,
        "tphi": 282,
        "wtheta": 28,
        "wphi": 52,
    }
    seabed_echo_mask = create_seabed_mask(
        source_Sv,
        method="blackwell",
        parameters=rapidkrill_seabed_echo_mask_params,
    )
    seabed_echo_mask = add_metadata_to_mask(
        mask=seabed_echo_mask,
        metadata={
            "mask_type": "false_seabed",
            "method": "blackwell",
            "parameters": dict_to_formatted_list(rapidkrill_seabed_echo_mask_params),
        },
    )

    masks = [transient_mask, impulse_mask, attenuation_mask, seabed_mask, seabed_echo_mask]
    Sv_mask = attach_masks_to_dataset(source_Sv, masks)
    return Sv_mask


def create_default_noise_masks_oceanstream(source_Sv: xarray.Dataset):
    """
    A function that creates noise masks for a given Sv dataset using default methods for oceanstream

    Parameters:
    - source_Sv (xarray.Dataset): the dataset to which the masks will be attached.

    Returns:
    - xarray.Dataset: a dataset with the same dimensions as the original,
    containing the original data and five masks: mask_transient, mask_impulse,
    mask_attenuated, mask_false_seabed, mask_seabed

    Notes:
    - To effectively utilize the `blackwell` or `blackwell_mod` methods for seabed detection,
    it's essential that the `source_Sv` dataset includes the `split-beam angle` parameters.
    Specifically, ensure that your input `source_Sv` contains
    both the `angle_alongship` and `angle_athwartship` variables.
    Absence of these variables leads to errors .
    """
    oceanstream_transient_mask_params = {
        "m": 5,
        "n": 20,
        "thr": 20,
        "excludeabove": 250,
        "operation": "percentile15",
    }
    transient_mask = create_transient_mask(
        source_Sv, parameters=oceanstream_transient_mask_params, method="ryan"
    )
    transient_mask = add_metadata_to_mask(
        mask=transient_mask,
        metadata={
            "mask_type": "transient",
            "method": "ryan",
            "parameters": dict_to_formatted_list(oceanstream_transient_mask_params),
        },
    )

    oceanstream_attenuation_mask_params = {
        "r0": 180,
        "r1": 280,
        "n": 30,
        "m": None,
        "thr": -6,
        "start": 0,
        "offset": 0,
    }
    attenuation_mask = create_attenuation_mask(
        source_Sv, parameters=oceanstream_attenuation_mask_params, method="ryan"
    )
    attenuation_mask = add_metadata_to_mask(
        mask=attenuation_mask,
        metadata={
            "mask_type": "attenuation",
            "method": "ryan",
            "parameters": dict_to_formatted_list(oceanstream_attenuation_mask_params),
        },
    )

    oceanstream_impulse_mask_param = {"thr": 10, "m": 5, "n": 1}
    impulse_mask = create_impulse_mask(
        source_Sv, parameters=oceanstream_impulse_mask_param, method="ryan"
    )
    impulse_mask = add_metadata_to_mask(
        mask=impulse_mask,
        metadata={
            "mask_type": "impulse",
            "method": "ryan",
            "parameters": dict_to_formatted_list(oceanstream_impulse_mask_param),
        },
    )

    oceanstream_seabed_echo_mask_params = {
        "theta": None,
        "phi": None,
        "r0": 10,
        "r1": 1000,
        "tSv": -75,
        "ttheta": 702,
        "tphi": 282,
        "wtheta": 28,
        "wphi": 52,
        "rlog": None,
        "tpi": None,
        "freq": None,
        "rank": 50,
    }
    seabed_echo_mask = create_seabed_mask(
        source_Sv,
        method="blackwell_mod",
        parameters=oceanstream_seabed_echo_mask_params,
    )
    seabed_echo_mask = add_metadata_to_mask(
        mask=seabed_echo_mask,
        metadata={
            "mask_type": "false_seabed",
            "method": "blackwell_mod",
            "parameters": dict_to_formatted_list(oceanstream_seabed_echo_mask_params),
        },
    )

    oceanstream_seabed_mask_params = {
        "r0": 10,
        "r1": 1000,
        "roff": 0,
        "thr": -40,
        "ec": 1,
        "ek": (1, 3),
        "dc": 10,
        "dk": (3, 7),
    }
    seabed_mask = create_seabed_mask(
        source_Sv,
        method="ariza",
        parameters=oceanstream_seabed_mask_params,
    )
    seabed_mask = add_metadata_to_mask(
        mask=seabed_mask,
        metadata={
            "mask_type": "seabed",
            "method": "ariza",
            "parameters": dict_to_formatted_list(oceanstream_seabed_mask_params),
        },
    )

    masks = [transient_mask, impulse_mask, attenuation_mask, seabed_echo_mask, seabed_mask]
    Sv_mask = attach_masks_to_dataset(source_Sv, masks)
    return Sv_mask


def create_noise_masks_oceanstream(source_Sv: xarray.Dataset):
    """
    A function that creates noise masks for a given Sv dataset using default methods for oceanstream

    Parameters:
    - source_Sv (xarray.Dataset): the dataset to which the masks will be attached.

    Returns:
    - xarray.Dataset: a dataset with the same dimensions as the original,
    containing the original data and five masks: mask_transient, mask_impulse,
    mask_attenuated, mask_false_seabed, mask_seabed

    Notes:
    - To effectively utilize the `blackwell` or `blackwell_mod` methods for seabed detection,
    it's essential that the `source_Sv` dataset includes the `split-beam angle` parameters.
    Specifically, ensure that your input `source_Sv` contains
    both the `angle_alongship` and `angle_athwartship` variables.
    Absence of these variables leads to errors .
    """
    oceanstream_transient_mask_params = {
        "r0": 200,
        "r1": 1000,
        "n": 5,
        "thr": [2, 0],
        "roff": 250,
        "jumps": 5,
        "maxts": -35,
        "start": 0,
    }
    transient_mask = create_transient_mask(
        source_Sv, parameters=oceanstream_transient_mask_params, method="fielding"
    )

    transient_mask = add_metadata_to_mask(
        mask=transient_mask,
        metadata={
            "mask_type": "transient",
            "method": "ryan",
            "parameters": dict_to_formatted_list(oceanstream_transient_mask_params),
        },
    )

    oceanstream_attenuation_mask_params = {
        "r0": 180,
        "r1": 280,
        "n": 5,
        "m": None,
        "thr": -5,
        "start": 0,
        "offset": 0,
    }

    attenuation_mask = create_attenuation_mask(
        source_Sv, parameters=oceanstream_attenuation_mask_params, method="ryan"
    )
    attenuation_mask = add_metadata_to_mask(
        mask=attenuation_mask,
        metadata={
            "mask_type": "attenuation",
            "method": "ryan",
            "parameters": dict_to_formatted_list(oceanstream_attenuation_mask_params),
        },
    )

    oceanstream_impulse_mask_param = {"thr": 3, "m": 3, "n": 1}
    impulse_mask = create_impulse_mask(
        source_Sv, parameters=oceanstream_impulse_mask_param, method="ryan"
    )
    impulse_mask = add_metadata_to_mask(
        mask=impulse_mask,
        metadata={
            "mask_type": "impulse",
            "method": "ryan",
            "parameters": dict_to_formatted_list(oceanstream_impulse_mask_param),
        },
    )

    masks = [transient_mask, impulse_mask, attenuation_mask]
    Sv_mask = attach_masks_to_dataset(source_Sv, masks)
    return Sv_mask
