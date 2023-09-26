import numpy as np
import pytest

from oceanstream.L2_calibrated_data.background_noise_remover import apply_remove_background_noise
from oceanstream.L2_calibrated_data.sv_computation import compute_sv


def test_apply_remove_background_noise(ed_ek_60_for_Sv):
    sv_echopype_EK60 = compute_sv(ed_ek_60_for_Sv)
    ds_Sv = apply_remove_background_noise(sv_echopype_EK60)
    assert np.nanmean(ds_Sv["Sv"].values) == pytest.approx(-72.7698338137907, 0.0001)
    assert np.nanmin(ds_Sv["Sv"].values) == pytest.approx(-156.02047944545484, 0.0001)
    assert np.nanmean(ds_Sv["Sv_with_background_noise"].values) == pytest.approx(
        np.nanmean(sv_echopype_EK60["Sv"].values), 0.0001
    )
