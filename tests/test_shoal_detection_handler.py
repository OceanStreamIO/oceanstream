import echopype as ep
import numpy as np
import pytest
import xarray as xr

from oceanstream.L2_calibrated_data.background_noise_remover import apply_remove_background_noise
from oceanstream.L2_calibrated_data.sv_computation import compute_sv
from oceanstream.L3_regridded_data.shoal_detection_handler import (
    attach_shoal_mask_to_ds,
    combine_shoal_masks_multichannel,
    create_shoal_mask_multichannel,
)


def _count_false_values(mask: xr.DataArray) -> int:
    return mask.size - mask.sum().item()


def test_create_shoal_mask_multichannel(ed_ek_60_for_Sv):
    sv_echopype_EK60 = compute_sv(ed_ek_60_for_Sv)
    ds_Sv = apply_remove_background_noise(sv_echopype_EK60)
    mask, mask_ = create_shoal_mask_multichannel(ds_Sv)

    assert _count_false_values(mask) == 4453154
    assert _count_false_values(mask_) == 0


def test_combine_shoal_masks_multichannel(ed_ek_60_for_Sv):
    sv_echopype_EK60 = compute_sv(ed_ek_60_for_Sv)
    ds_Sv = apply_remove_background_noise(sv_echopype_EK60)
    mask, mask_ = create_shoal_mask_multichannel(ds_Sv)
    combined_masks = combine_shoal_masks_multichannel(mask, mask_)

    assert _count_false_values(combined_masks) == 4453154


def test_attach_shoal_mask_to_ds(ed_ek_60_for_Sv):
    sv_echopype_EK60 = compute_sv(ed_ek_60_for_Sv)
    ds_Sv = apply_remove_background_noise(sv_echopype_EK60)
    ds_Sv_shoal_combined = attach_shoal_mask_to_ds(ds_Sv)
    ds_Sv_shoal_combined = ep.mask.apply_mask(
        ds_Sv_shoal_combined, ds_Sv_shoal_combined["mask_shoal"]
    )
    assert np.nanmean(ds_Sv_shoal_combined["Sv"].values) == pytest.approx(
        -60.747615128417785, 0.0001
    )
