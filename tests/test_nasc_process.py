import pytest

from oceanstream.exports.csv.csv_export_nasc import *

# @pytest.mark.ignore
def test_compute_per_dataset_nasc(ek_60_Sv_full_denoised):
    dataset = ek_60_Sv_full_denoised
    nasc = base_nasc_data(dataset)
    short_nasc = base_nasc_data(dataset, True, "fish_NASC")

    assert len(nasc) == 21
    assert len(short_nasc) == 3
    assert "fish_NASC_38000.0" in short_nasc

# @pytest.mark.ignore
def test_compute_masked_nasc(ek_60_Sv_shoal):
    dataset = ek_60_Sv_shoal
    fish_nasc = mask_nasc_data(dataset, {"mask_shoal": False}, True, "fish_NASC")
    assert fish_nasc['fish_NASC_38000.0'] == pytest.approx(103252307.9526562, 0.0001)

# @pytest.mark.ignore
def test_compute_full_nasc(ek_60_Sv_shoal):
    dataset = ek_60_Sv_shoal
    nasc = full_nasc_data(dataset, BASE_NASC_PARAMETERS)
    assert len(nasc) == 24
    assert nasc['fish_NASC_38000.0'] == pytest.approx(103252307.9526562, 0.0001)
