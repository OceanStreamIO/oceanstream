from pathlib import Path

import xarray as xr
from echopype.mask.api import apply_mask
from pandas import DataFrame

from oceanstream.exports.nasc_computation import compute_per_dataset_nasc

BASE_NASC_PARAMETERS = [
    {"masks": {"mask_shoal": False}, "abbreviated": True, "root_name": "fish_NASC"}
]


def base_nasc_data(Sv: xr.Dataset, abbreviated: bool = False, root_name: str = None):
    """
    Given a Sv dataset, returns a dataframe containing nasc data for it

    Parameters:
    - Sv: xr.Dataset - Sv dataset
    - abbreviated: bool - do we keep all the info, or just the NASC
    - root_name: str - name to rename NASC by, if needed

    Returns:
    - a dictionary of nasc data

    Example:
        >>> base_nasc_data(Sv)
    """

    nasc_list = compute_per_dataset_nasc(Sv)
    nasc = nasc_list["NASC_dataset"]
    maximum_distance = nasc_list["maximum_distance"]
    maximum_depth = nasc_list["maximum_depth"]
    samples = len(Sv.ping_time) * len(Sv.range_sample)  # temp

    metadata = {}
    if abbreviated is False:
        metadata["filename"] = Path(Sv.source_filenames.values.item()).stem
        metadata["start_lat"] = nasc.attrs["geospatial_lat_min"]
        metadata["end_lat"] = nasc.attrs["geospatial_lat_max"]
        metadata["start_lon"] = nasc.attrs["geospatial_lon_min"]
        metadata["end_lon"] = nasc.attrs["geospatial_lon_max"]
        metadata["start_time"] = nasc.attrs["time_coverage_start"]
        metadata["end_time"] = nasc.attrs["time_coverage_start"]
        metadata["start_ping"] = (0,)
        metadata["end_ping"] = len(Sv.ping_time)
        metadata["NASC_st_range"] = 0
        metadata["NASC_en_range"] = maximum_depth
        metadata["maximum_distance"] = maximum_distance

    nasc_frame = nasc[["frequency_nominal", "NASC"]].to_dataframe().reset_index(drop=True)
    if root_name is not None:
        nasc_frame.rename(columns={"NASC": root_name}, inplace=True)
    if abbreviated is False:
        nasc_frame["Observed_samples"] = samples
        nasc_frame["Valid_samples"] = samples

    nasc_melted = nasc_frame.melt(id_vars="frequency_nominal")
    nasc_melted["name"] = (
        nasc_melted["variable"] + "_" + nasc_melted["frequency_nominal"].astype(str)
    )
    nasc_data = {r["name"]: r["value"] for index, r in nasc_melted.iterrows()}
    metadata.update(nasc_data)
    return metadata


def mask_nasc_data(Sv: xr.Dataset, masks={}, abbreviated: bool = False, root_name: str = None):
    """
    Given a Sv dataset and a dictionary where the keys are mask names and the values are true/false
    it applies those masks to it reverted or not, based on the value, and returns a dict of nasc data

    Parameters:
    - Sv: xr.Dataset - Sv dataset
    - masks: {} - dictionary of mask names and True/False on whether we negate them
    - abbreviated: bool - do we keep all the info, or just the NASC
    - root_name: str - name to rename NASC by, if needed

    Returns:
    - a dictionary of nasc data

    Example:
        >>> base_nasc_data(Sv)
    """
    Sv = Sv.copy(deep=True)
    for mask in masks.keys():
        if mask not in Sv:
            raise ValueError(f"Mask {mask} does not exist in the dataset")
        else:
            if masks[mask]:
                Sv[mask] = ~Sv[mask]
        Sv = apply_mask(Sv, Sv[mask])
    return base_nasc_data(Sv, abbreviated, root_name)


def full_nasc_data(Sv: xr.Dataset, parameter_list=BASE_NASC_PARAMETERS):
    """
    Given a Sv dataset and a list of potential parameters for mask_nasc_data,
    it returns a dictionary containing nasc data for all possibilities.
    Useful if we want to specify whether we take fish nasc, krill nasc etc

    Parameters:
    - Sv: xr.Dataset - Sv dataset
    - parameter_list: list of parameters to pass to mask_nasc_data

    Returns:
    - a dictionary of nasc data

    Example:
        >>> full_nasc_data(Sv)
    """
    base = base_nasc_data(Sv)
    for parameters in parameter_list:
        masks = parameters["masks"]
        abbreviated = parameters["abbreviated"]
        root_name = parameters["root_name"]
        extra = mask_nasc_data(Sv, masks, abbreviated, root_name)
        base.update(extra)
    return base


def write_nasc_to_csv(nasc, filename):
    """
    Given a nasc dict and a filename, it exports it as csv to the filename

    Parameters:
    - nasc: {}
        the dict containing nasc metadata
    - filename: str
        The file name to use.

    Returns:
    - None
    """
    df = DataFrame(nasc)
    df.to_csv(filename, index=False)
