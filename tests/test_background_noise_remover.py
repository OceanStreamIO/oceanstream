import numpy as np
import pytest

from oceanstream.L2_calibrated_data.background_noise_remover import apply_remove_background_noise
from oceanstream.L2_calibrated_data.sv_computation import compute_sv


def test_apply_remove_background_noise(ed_ek_60_for_Sv):
    sv_echopype_EK60 = compute_sv(ed_ek_60_for_Sv)
    ds_Sv = apply_remove_background_noise(sv_echopype_EK60)
    assert np.nanmean(ds_Sv["Sv_noise"].values) == pytest.approx(-96.67702294789203, 0.0001)
    assert np.nanmax(ds_Sv["Sv_noise"].values) == pytest.approx(-69.21781259163029, 0.0001)
    assert np.nanmean(ds_Sv["Sv_corrected"].values) == pytest.approx(-72.7698338137907, 0.0001)
    assert np.nanmin(ds_Sv["Sv_corrected"].values) == pytest.approx(-156.02047944545484, 0.0001)
