import scipy.ndimage as nd_img
import xarray as xr


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
