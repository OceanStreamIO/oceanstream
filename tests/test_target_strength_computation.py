import numpy as np
import pytest

from oceanstream.L2_calibrated_data import target_strength_computation


def test_ctarget_strength_computation(ed_ek_60_for_Sv):
    TS = target_strength_computation.compute_target_strength(ed_ek_60_for_Sv, encode_mode="power")
    val = np.nanmean(TS["TS"].values)
    assert val == pytest.approx(-68.06057158474684, 0.0001)
