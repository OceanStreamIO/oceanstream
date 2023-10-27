import scipy.ndimage as nd_img
import xarray as xr
from echopype.mask.api import apply_mask

from oceanstream.utils import haversine


def split_shoal_mask(Sv: xr.Dataset):
    """
    Given a Sv dataset with an existing shoal mask, generates a list of
    individual masks for each shoal

    Parameters:
    - Sv: xr.Dataset - Sv dataset with an existing shoal mask

    Returns:
    - [xr.DataArray]: list of individual shoal masks

    Example:
        >>> split_shoal_mask(Sv)
    """
    all_shoals = Sv["mask_shoal"]
    labelled = nd_img.label(all_shoals)
    la = labelled[0]
    ls = labelled[1]
    shoals = []
    for i in range(1, ls + 1):
        shoal = xr.DataArray(
            data=(la == i),
            dims=all_shoals.dims,
            coords=all_shoals.coords,
        )
        shoal.attrs["label"] = i
        shoals.append(shoal)
    return shoals


def process_single_shoal(Sv: xr.Dataset, mask: xr.DataArray):
    """
    Given a Sv dataset and a shoal mask containing a single shoal, returns a
    dataframe containing shoal metadata for each channel

    Parameters:
    - Sv: xr.Dataset - Sv dataset
    - mask: xr.DataArray - single-shoal mask

    Returns:
    - [pd.Dataframe]: a list of single-row-per-channel dictionaries containing shoal metadata

    Example:
        >>> process_single_shoal(Sv, mask)
    """
    channels = Sv["channel"]
    results = [process_single_shoal_channel(Sv, mask, c) for c in channels]
    results = [r for r in results if r is not None]
    if results == []:
        return None
    return results


def process_single_shoal_channel(Sv: xr.Dataset, mask: xr.DataArray, channel: str):
    """
    Given a Sv dataset, a shoal mask containing a single shoal and the desired channel,
    returns a dataframe containing shoal metadata for that specific channel

    Parameters:
    - Sv: xr.Dataset - Sv dataset
    - mask: xr.DataArray - single-shoal mask
    - channel: str - channel

    Returns:
    - dict: a dictionary containing shoal metadata

    Example:
        >>> process_single_shoal_channel(Sv, mask, channel)
    """
    mc = mask.sel(channel=channel)
    Sv_sel = Sv.sel(channel=channel)
    Sv_masked = apply_mask(Sv_sel.copy(deep=True), mc)

    # create a dataset that has the mask instead of Sv
    md = Sv_masked.copy(deep=True)
    md["Sv"] = ~md["Sv"].isnull()

    Sv_mean = Sv_masked.Sv.mean(skipna=True).values
    frequency = Sv_masked.frequency_nominal.values
    area = mc.sum().values
    if area == 0:
        return None
    filename = md.source_filenames.values
    label = mc.attrs["label"]

    ping_true = md["Sv"].any(dim="range_sample")
    range_true = md["Sv"].any(dim="ping_time")
    subset_md = md.sel(ping_time=ping_true, range_sample=range_true)

    # TODO figure out exactly how the shiny tool does plotting
    # bbox_0 = subset_md.ping_time.min().values
    # bbox_2 = subset_md.ping_time.max().values
    # bbox_1 = subset_md.range_sample.min().values
    # bbox_3 = subset_md.range_sample.max().values
    # centroid_0 = (bbox_0 + bbox_2) / 2
    # centroid_1 = (bbox_1 + bbox_3) / 2

    bbox_0 = 0
    bbox_1 = 0
    bbox_2 = 0
    bbox_3 = 0
    centroid_0 = (bbox_0 + bbox_2) / 2
    centroid_1 = (bbox_1 + bbox_3) / 2

    npings = len(subset_md.ping_time)
    nsamples = len(subset_md.range_sample)
    mean_range = subset_md.range_sample.mean().values

    start_time = subset_md.ping_time.min().values
    end_time = subset_md.ping_time.max().values
    start_range = subset_md.range_sample.min().values
    end_range = subset_md.range_sample.max().values

    start_lat = subset_md.latitude[0].values
    end_lat = subset_md.latitude[-1].values
    start_lon = subset_md.longitude[0].values
    end_lon = subset_md.longitude[-1].values
    length_meters = haversine("m", start_lat, end_lat, start_lon, end_lon)

    return_dict = {
        "label": label,
        "frequency": frequency,
        "filename": filename,
        "area": area,
        "bbox.0": bbox_0,
        "bbox.1": bbox_1,
        "bbox.2": bbox_2,
        "bbox.3": bbox_3,
        "centroid.0": centroid_0,
        "centroid.1": centroid_1,
        "Sv_mean": Sv_mean,
        "npings": npings,
        "nsamples": nsamples,
        "corrected_length": length_meters,
        "mean_range": mean_range,
        "start_range": start_range,
        "end_range": end_range,
        "start_time": start_time,
        "end_time": end_time,
        "start_lat": start_lat,
        "end_lat": end_lat,
        "start_lon": start_lon,
        "end_lon": end_lon,
    }

    return return_dict


def process_shoals(Sv: xr.Dataset):
    """
    Given a Sv dataset with an existing shoal mask, generates a list of
    individual masks for each shoal

    Parameters:
    - Sv: xr.Dataset - Sv dataset with an existing shoal mask

    Returns:
    - [xr.DataArray]: list of individual shoal masks

    Example:
        >>> split_shoal_mask(Sv)
    """
    masks = split_shoal_mask(Sv)
    dicts = [process_single_shoal(Sv, mask) for mask in masks]
    results = [item for sublist in dicts for item in sublist]
    results = [r for r in results if r is not None]
    return results