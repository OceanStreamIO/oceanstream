import numpy as np
import pytest

from oceanstream.L2_calibrated_data.background_noise_remover import apply_remove_background_noise
from oceanstream.L2_calibrated_data.sv_computation import compute_sv
from oceanstream.L3_regridded_data.frequency_differencing_handler import apply_freq_diff


def test_apply_remove_background_noise(ed_ek_60_for_Sv):
    sv_echopype_EK60 = compute_sv(ed_ek_60_for_Sv)
    ds_Sv = apply_remove_background_noise(sv_echopype_EK60)
    chanA = "GPT 120 kHz 00907205a6d0 4-1 ES120-7C"
    chanB = "GPT  38 kHz 009072058146 2-1 ES38B"
    ds_Sv_interval = apply_freq_diff(
        ds=ds_Sv,
        chanA=chanA,
        chanB=chanB,
        interval_start_operator=">=",
        interval_start_value="2.0",
        interval_end_operator="<=",
        interval_end_value="16.0",
    )
    ds_Sv_single = apply_freq_diff(
        ds=ds_Sv, chanA=chanA, chanB=chanB, single_operator=">=", single_value="2.0"
    )
    assert np.nanmean(ds_Sv_interval["Sv"].values) == pytest.approx(-72.54676167765183, 0.0001)
    assert np.nanmin(ds_Sv_single["Sv"].values) == pytest.approx(-140.24009439945064, 0.0001)
    try:
        apply_freq_diff(ds=ds_Sv, chanA=chanA, chanB=chanB)
    except ValueError:
        pass
