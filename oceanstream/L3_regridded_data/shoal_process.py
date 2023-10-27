import scipy.ndimage as nd_img
import xarray as xr
from echopype.mask.api import apply_mask


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
    - [pd.Dataframe]: a single-row-per-channel dataframe containing shoal metadata

    Example:
        >>> process_single_shoal(Sv, mask)
    """
    channels = Sv["channel"]
    channels = [channels[1]]  # temp #TODO remove after dev
    results = [process_single_shoal_channel(Sv, mask, c) for c in channels]
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
    - [pd.Dataframe]: a single-row dataframe containing shoal metadata

    Example:
        >>> process_single_shoal_channel(Sv, mask, channel)
    """
    mc = mask.sel(channel=channel)
    Sv_sel = Sv.sel(channel=channel)
    Sv_masked = apply_mask(Sv_sel.copy(deep=True), mc)

    # create a dataset that has the mask instead of Sv
    md = Sv_masked.copy(deep=True)
    md["Sv"] = ~md["Sv"].isnull()

    # Sv_mean = Sv_masked["Sv"].mean(skipna=True).values
    # frequency = Sv_masked["frequency_nominal"].values
    # area = mc.sum().values
    return Sv.data_vars
