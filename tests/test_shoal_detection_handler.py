import echopype as ep
import numpy as np
import pytest
import xarray as xr

from oceanstream.exports.shoals.shoal_detection_handler import (
    attach_shoal_mask_to_ds,
    create_shoal_mask_multichannel,
)


def _count_false_values(mask: xr.DataArray) -> int:
    print(mask)
    return mask.size - mask.sum().compute().item()


@pytest.fixture(scope="session")
def shoal_masks(ek_60_Sv_denoised):
    mask = create_shoal_mask_multichannel(ek_60_Sv_denoised)
    return mask


@pytest.mark.ignore
def test_create_shoal_mask_multichannel(ek_60_Sv_denoised):
    mask = create_shoal_mask_multichannel(ek_60_Sv_denoised)
    assert _count_false_values(mask) == 4471604


@pytest.mark.ignore
def test_attach_shoal_mask_to_ds(ek_60_Sv_denoised):
    ds_Sv_shoal_combined = attach_shoal_mask_to_ds(ek_60_Sv_denoised)
    ds_Sv_shoal_combined = ep.mask.apply_mask(
        ds_Sv_shoal_combined, ds_Sv_shoal_combined["mask_shoal"]
    )
    assert np.nanmean(ds_Sv_shoal_combined["Sv"].values) == pytest.approx(
        -61.21094022368077, 0.0001
    )
