import numpy as np
import pytest

from oceanstream.L2_calibrated_data.background_noise_remover import apply_remove_background_noise


def test_apply_remove_background_noise(enriched_ek60_Sv):
    ds_Sv = apply_remove_background_noise(enriched_ek60_Sv)
    assert np.nanmean(ds_Sv["Sv"].values) == pytest.approx(-72.7698338137907, 0.0001)
    assert np.nanmin(ds_Sv["Sv"].values) == pytest.approx(-156.02047944545484, 0.0001)
    assert np.nanmean(ds_Sv["Sv_with_background_noise"].values) == pytest.approx(
        np.nanmean(enriched_ek60_Sv["Sv"].values), 0.0001
    )
