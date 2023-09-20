import numpy as np
import pytest

from oceanstream.L2_calibrated_data.sv_computation import compute_sv
from oceanstream.L2_calibrated_data.sv_dataset_extension import enrich_sv_dataset


def test_enrich_sv_dataset_depth_mean(ed_ek_60_for_Sv):
    sv_echopype_EK60 = compute_sv(ed_ek_60_for_Sv)
    enriched_sv = enrich_sv_dataset(
        sv_echopype_EK60, ed_ek_60_for_Sv, depth_offset=200, waveform_mode="CW", encode_mode="power"
    )
    assert np.nanmean(enriched_sv.depth.values) == pytest.approx(299.87710562283445, 0.0001)


def test_enhance_sv_location_mean(ed_ek_60_for_Sv):
    sv_echopype_EK60 = compute_sv(ed_ek_60_for_Sv)
    enriched_sv = enrich_sv_dataset(
        sv_echopype_EK60, ed_ek_60_for_Sv, depth_offset=200, waveform_mode="CW", encode_mode="power"
    )
    assert np.nanmean(enriched_sv.latitude.values) == pytest.approx(44.705425101593775, 0.0001)
    assert np.nanmean(enriched_sv.longitude.values) == pytest.approx(-124.34924860021844, 0.0001)


def test_enrich_sv_dataset_splitbeam_angle_max(ed_ek_60_for_Sv):
    sv_echopype_EK60 = compute_sv(ed_ek_60_for_Sv)
    enriched_sv = enrich_sv_dataset(
        sv_echopype_EK60, ed_ek_60_for_Sv, depth_offset=200, waveform_mode="CW", encode_mode="power"
    )
    assert np.nanmax(enriched_sv.angle_alongship.values) == pytest.approx(
        13.057721067462003, 0.0001
    )
    assert np.nanmax(enriched_sv.angle_athwartship.values) == pytest.approx(
        12.647721071038282, 0.0001
    )


def test_enrich_sv_dataset_warning(ed_ek_60_for_Sv):
    with pytest.warns(UserWarning):
        sv_echopype_EK60 = compute_sv(ed_ek_60_for_Sv)
        enrich_sv_dataset(sv_echopype_EK60, ed_ek_60_for_Sv, depth_offset=200)
