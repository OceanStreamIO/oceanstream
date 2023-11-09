from typing import Dict, Union

import echopype as ep
import numpy as np
import xarray as xr


def compute_per_dataset_nasc(Sv_ds: xr.Dataset) -> Dict[str, Union[xr.Dataset, str]]:
    """
    Compute NASC (Nautical Area Scattering Coefficient) for an entire Sv dataset using echopype.

    This function determines the maximum depth and distance from the given Sv dataset
    and computes NASC using these as bin sizes for echopype's `compute_NASC` function.
    The binning process will produce one bin per channel in the dataset.

    Parameters:

    Sv_ds : xr.Dataset
        A cleaned dataset containing Sv data that has been preprocessed to remove noise.
        The dataset should have `latitude`, `longitude`, and `depth` data variables.

    Returns:

    Dict[str, Union[xr.Dataset, str]]
        A dictionary containing:
        - "NASC_dataset": the computed NASC values as an xarray dataset
        - "maximum_depth": a string indicating the maximum depth used for binning
        - "maximum_distance": a string indicating the maximum distance used for binning

    Notes:

    Ensure that the Sv dataset is free of noise before using this function.
    The computation relies on the `compute_NASC` function from the `echopype` library,
    which is based on the Echoview algorithm PRC_NASC.

    See Also:

    echopype.commongrid.api.compute_NASC: The echopype function used for the underlying NASC computation.
    """

    # Get the maximum distance from the Sv dataset
    dist = ep.commongrid.utils.get_distance_from_latlon(Sv_ds)
    max_dist = np.nanmax(dist)
    # max_dist = dist.max()
    max_dist_str = str(max_dist) + "nmi"

    # Get the maximum depth from the Sv dataset
    max_depth = np.nanmax(Sv_ds["depth"].values)
    # max_depth = Sv_ds.depth.values.max()
    max_depth_str = str(max_depth) + "m"

    # Compute NASC using the determined max depth and max distance - one bin per channel
    nasc_ep = ep.commongrid.api.compute_NASC(Sv_ds, range_bin=max_depth_str, dist_bin=max_dist_str)

    return {
        "NASC_dataset": nasc_ep,
        "maximum_depth": max_depth_str,
        "maximum_distance": max_dist_str,
    }
