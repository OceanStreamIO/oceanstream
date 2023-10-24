
from oceanstream.L2_calibrated_data.sv_computation import compute_sv
from oceanstream.L2_calibrated_data.sv_dataset_extension import enrich_sv_dataset
from oceanstream.L3_regridded_data.csv_export_from_Sv import *


def test_haversine():
    lat1 = 44.707938
    lon1 = -124.343030
    lat2 = 44.707918
    lon2 = -124.343044
    assert haversine(lat1, lon1, lat2, lon2) == 0.001200809214817291


def test_create_location(ed_ek_60_for_Sv):
    sv_echopype_EK60 = compute_sv(ed_ek_60_for_Sv)
    enriched_sv = enrich_sv_dataset(
        sv_echopype_EK60, ed_ek_60_for_Sv, depth_offset=200, waveform_mode="CW", encode_mode="power"
    )
    res = create_location(enriched_sv)
    assert res.shape == (1932, 4)
    assert res["knt"][1931] == 0.8838246707925663