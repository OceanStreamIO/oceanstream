from oceanstream.L3_regridded_data.csv_export_from_Sv import create_location, create_Sv


def test_create_location(enriched_ek60_Sv):
    enriched_sv = enriched_ek60_Sv
    res = create_location(enriched_sv)
    assert res.shape == (1932, 4)
    assert res["knt"][1931] == 1.7561833282548402


def test_create_Sv(enriched_ek60_Sv):
    channel = enriched_ek60_Sv["channel"][1]
    enriched_sv = enriched_ek60_Sv
    res = create_Sv(enriched_sv, channel)
    assert res.shape == (1055, 1932)
