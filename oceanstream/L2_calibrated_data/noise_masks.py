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

RAPIDKRILL_MASK_PARAMETERS = {
    "transient": {
        "method": "ryan",
        "params": {
            "m": 5,
            # "n": 20,
            "n": 5,
            "thr": 20,
            "excludeabove": 250,
            "operation": "percentile15",
        },
    },
    "attenuation": {
        "method": "ryan",
        "params": {
            "r0": 180,
            "r1": 280,
            "n": 30,
            "m": None,
            "thr": -6,
            "start": 0,
            "offset": 0,
        },
    },
    "impulse": {"method": "ryan", "params": {"thr": 10, "m": 5, "n": 1}},
    "seabed": {
        "method": "ariza",
        "params": {
            "r0": 10,
            "r1": 1000,
            "roff": 0,
            "thr": -40,
            "ec": 1,
            "ek": (1, 3),
            "dc": 10,
            "dk": (3, 7),
        },
    },
    "false_seabed": {
        "method": "blackwell",
        "params": {
            "theta": None,
            "phi": None,
            "r0": 10,
            "r1": 1000,
            "tSv": -75,
            "ttheta": 702,
            "tphi": 282,
            "wtheta": 28,
            "wphi": 52,
        },
    },
}


OCEANSTREAM_MASK_PARAMETERS = {
    "transient": {
        "method": "ryan",
        "params": {
            "m": 5,
            # "n": 20,
            "n": 5,
            "thr": 20,
            "excludeabove": 250,
            "operation": "percentile15",
        },
    },
    "attenuation": {
        "method": "ryan",
        "params": {
            "r0": 180,
            "r1": 280,
            "n": 5,
            "m": None,
            "thr": -5,
            "start": 0,
            "offset": 0,
        },
    },
    "impulse": {"method": "ryan", "params": {"thr": 3, "m": 3, "n": 1}},
    "seabed": {
        "method": "ariza",
        "params": {
            "r0": 10,
            "r1": 1000,
            "roff": 0,
            "thr": -35,
            "ec": 15,
            "ek": (1, 3),
            "dc": 150,
            "dk": (1, 3),
        },
    },
    "false_seabed": {
        "method": "blackwell_mod",
        "params": {
            "theta": None,
            "phi": None,
            "r0": 10,
            "r1": 1000,
            "tSv": -75,
            "ttheta": 702,
            "tphi": 282,
            "wtheta": 28,
            "wphi": 52,
        },
    },
}

TEST_MASK_PARAMETERS = {
    "transient": {
        "method": "ryan",
        "params": {
            "m": 5,
            "n": 5,
            "thr": 20,
            "excludeabove": 250,
            "operation": "mean",
        },
    },
    "attenuation": {
        "method": "ryan",
        "params": {
            "r0": 180,
            "r1": 280,
            "n": 5,
            "m": None,
            "thr": -5,
            "start": 0,
            "offset": 0,
        },
    },
    "impulse": {"method": "ryan", "params": {"thr": 3, "m": 3, "n": 1}},
    "seabed": {
        "method": "ariza",
        "params": {
            "r0": 10,
            "r1": 1000,
            "roff": 0,
            "thr": -40,
            "ec": 1,
            "ek": (1, 3),
            "dc": 10,
            "dk": (3, 7),
        },
    },
    "false_seabed": {
        "method": "blackwell",
        "params": {
            "theta": None,
            "phi": None,
            "r0": 10,
            "r1": 1000,
            "tSv": -75,
            "ttheta": 702,
            "tphi": 282,
            "wtheta": 28,
            "wphi": 52,
        },
    },
}

OCEANSTREAM_NOISE_MASK_PARAMETERS = {
    k: OCEANSTREAM_MASK_PARAMETERS[k] for k in ["transient", "attenuation", "impulse"]
}
OCEANSTREAM_SEABED_MASK_PARAMETERS = {
    k: OCEANSTREAM_MASK_PARAMETERS[k] for k in ["seabed", "false_seabed"]
}


MASK_PARAMETERS = {
    "method": "ryan",
    "params": {"thr": 3, "m": 3, "n": 1},
}


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


def create_mask(source_Sv: xarray.Dataset, mask_type="impulse", params=MASK_PARAMETERS):
    """
    A function that creates a single noise mask for a given dataset

    Parameters:
    - source_Sv (xarray.Dataset): the dataset to which the masks will be attached.
    - mask type (str): type of mask
    - params (dict): a dictionary of mask parameters containing type and

    Returns:
    - xarray.DataArray: the required mask
    """
    mask_map = {
        "transient": create_transient_mask,
        "impulse": create_impulse_mask,
        "attenuation": create_attenuation_mask,
        "seabed": create_seabed_mask,
        "false_seabed": create_seabed_mask,
    }
    method = params["method"]
    parameters = params["params"]

    mask = mask_map[mask_type](source_Sv, parameters=parameters, method=method)
    mask = add_metadata_to_mask(
        mask,
        metadata={
            "mask_type": mask_type,
            "method": "method",
            "parameters": dict_to_formatted_list(parameters),
        },
    )
    return mask


def create_multiple_masks(source_Sv: xarray.Dataset, params=TEST_MASK_PARAMETERS):
    """
    A function that creates multiple noise masks for a given Sv dataset

    Parameters:
    - source_Sv (xarray.Dataset): the dataset to which the masks will be attached.
    - params (dict): a dict of dictionaries of mask parameters

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
    masks = [create_mask(source_Sv, mask_type=k, params=params[k]) for k in params.keys()]
    Sv_mask = attach_masks_to_dataset(source_Sv, masks)
    return Sv_mask


def create_noise_masks_rapidkrill(source_Sv: xarray.Dataset, params=RAPIDKRILL_MASK_PARAMETERS):
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
    Sv_mask = create_multiple_masks(source_Sv, params)
    return Sv_mask


def create_default_noise_masks_oceanstream(
    source_Sv: xarray.Dataset, params=OCEANSTREAM_MASK_PARAMETERS
):
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
    Sv_mask = create_multiple_masks(source_Sv, params)
    return Sv_mask


def create_seabed_masks_oceanstream(
    source_Sv: xarray.Dataset, params=OCEANSTREAM_SEABED_MASK_PARAMETERS
):
    """
    A function that creates seabed masks for a given Sv dataset using default methods for oceanstream

    Parameters:
    - source_Sv (xarray.Dataset): the dataset to which the masks will be attached.

    Returns:
    - xarray.Dataset: a dataset with the same dimensions as the original,
    containing the original data and five masks: mask_transient, mask_impulse,
    mask_attenuated

    """
    Sv_mask = create_multiple_masks(source_Sv, params)
    return Sv_mask


def create_noise_masks_oceanstream(
    source_Sv: xarray.Dataset, params=OCEANSTREAM_NOISE_MASK_PARAMETERS
):
    """
    A function that creates noise masks for a given Sv dataset using default methods for oceanstream

    Parameters:
    - source_Sv (xarray.Dataset): the dataset to which the masks will be attached.

    Returns:
    - xarray.Dataset: a dataset with the same dimensions as the original,
    containing the original data and five masks: mask_transient, mask_impulse,
    mask_attenuated

    """
    Sv_mask = create_multiple_masks(source_Sv, params)
    return Sv_mask
