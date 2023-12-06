import pytest

from oceanstream.exports import nasc_computation


def test_compute_per_dataset_nasc(enriched_ek60_Sv):
    nasc_os = nasc_computation.compute_per_dataset_nasc(enriched_ek60_Sv)

    val = (
        nasc_os["NASC_dataset"]["NASC"]
        .sel(channel="GPT  18 kHz 009072058c8d 1-1 ES18-11")
        .values[0][0]
    )
    assert val == pytest.approx(25554438.181145363, 0.0001)
    assert nasc_os["maximum_depth"][0:3] == "199"
    assert nasc_os["maximum_distance"][0:3] == "3.2"
