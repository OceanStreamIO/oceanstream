import numpy as np
import pytest

from oceanstream.echodata.sv_computation import compute_sv
from oceanstream.echodata.sv_dataset_extension import (
    enrich_sv_dataset,
    add_seabed_depth
)
from oceanstream.denoise.noise_masks import (
    create_seabed_mask,
    attach_masks_to_dataset,
)
from oceanstream.utils import add_metadata_to_mask, dict_to_formatted_list


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


def test_add_seabed_depth(ed_ek_60_for_Sv):
    rapidkrill_seabed_mask_params = {
        "r0": 10,
        "r1": 1000,
        "roff": 0,
        "thr": -40,
        "ec": 1,
        "ek": (1, 3),
        "dc": 10,
        "dk": (3, 7),
    }
    source_Sv = enrich_sv_dataset(
        sv=compute_sv(ed_ek_60_for_Sv), echodata=ed_ek_60_for_Sv, waveform_mode="CW", encode_mode="power"
    )
    seabed_mask = create_seabed_mask(
        source_Sv,
        method="ariza",
        parameters=rapidkrill_seabed_mask_params,
    )
    seabed_mask = add_metadata_to_mask(
        mask=seabed_mask,
        metadata={
            "mask_type": "seabed",
            "method": "ariza",
            "parameters": dict_to_formatted_list(rapidkrill_seabed_mask_params),
        },
    )
    Sv_mask = attach_masks_to_dataset(source_Sv, [seabed_mask])
    res = add_seabed_depth(Sv_mask)
    res_sl = res["seabed_level"]
    assert res_sl.shape == (3, 1932)
    assert res_sl[0, 0] == 464
