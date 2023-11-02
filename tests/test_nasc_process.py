import pytest

from oceanstream.L3_regridded_data.csv_export_nasc import *


def test_compute_per_dataset_nasc(ek_60_Sv_full_denoised):
    dataset = ek_60_Sv_full_denoised
    nasc = base_nasc_data(dataset)
    short_nasc = base_nasc_data(dataset, True, "fish_NASC")

    assert len(nasc) == 21
    assert len(short_nasc) == 3
    assert "fish_NASC_38000.0" in short_nasc


def test_compute_masked_nasc(ek_60_Sv_shoal):
    dataset = ek_60_Sv_shoal
    fish_nasc = mask_nasc_data(dataset, {"mask_shoal": False}, True, "fish_NASC")
    assert fish_nasc['fish_NASC_38000.0'] == 148692889.40505505


def test_compute_full_nasc(ek_60_Sv_shoal):
    dataset = ek_60_Sv_shoal
    nasc = full_nasc_data(dataset, BASE_NASC_PARAMETERS)
    assert len(nasc) == 24
    assert nasc['fish_NASC_38000.0'] == 148692889.40505505
