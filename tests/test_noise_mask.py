import pytest

from oceanstream.L2_calibrated_data.noise_masks import (
    create_attenuation_mask,
    create_default_noise_masks_oceanstream,
    create_impulse_mask,
    create_noise_masks_rapidkrill,
    create_seabed_mask,
    create_transient_mask,
)
from oceanstream.L2_calibrated_data.sv_computation import compute_sv


def test_impulse(ed_ek_60_for_Sv):
    source_Sv = compute_sv(ed_ek_60_for_Sv)
    RYAN_DEFAULT_PARAMS = {"thr": 10, "m": 5, "n": 1}
    mask = create_impulse_mask(source_Sv, parameters=RYAN_DEFAULT_PARAMS)
    assert mask["channel"].shape == (3,)


@pytest.mark.ignore
def test_transient(sv_dataset_jr161):
    source_Sv = sv_dataset_jr161
    FIELDING_DEFAULT_PARAMS = {
        "r0": 200,
        "r1": 1000,
        "n": 5,
        "thr": [2, 0],
        "roff": 250,
        "jumps": 5,
        "maxts": -35,
        "start": 0,
    }
    mask_fielding = create_transient_mask(
        source_Sv, parameters=FIELDING_DEFAULT_PARAMS, method="fielding"
    )
    assert mask_fielding["channel"].shape == (3,)


def test_attenuation(ed_ek_60_for_Sv):
    DEFAULT_RYAN_PARAMS = {"r0": 180, "r1": 280, "n": 30, "thr": -6, "start": 0}
    source_Sv = compute_sv(ed_ek_60_for_Sv)
    mask = create_attenuation_mask(source_Sv, parameters=DEFAULT_RYAN_PARAMS)
    assert mask["channel"].shape == (3,)


def test_seabed(ed_ek_60_for_Sv):
    source_Sv = compute_sv(ed_ek_60_for_Sv)
    mask = create_seabed_mask(source_Sv)
    assert mask["channel"].shape == (3,)


@pytest.mark.ignore
def test_add_masks_rapidkrill(ed_ek_60_for_Sv):
    source_Sv = compute_sv(ed_ek_60_for_Sv)
    Sv_mask = create_noise_masks_rapidkrill(source_Sv)
    assert Sv_mask["mask_seabed"].attrs["mask_type"] == "seabed"


@pytest.mark.ignore
def test_add_masks_default_oceanstream(ed_ek_60_for_Sv):
    source_Sv = compute_sv(ed_ek_60_for_Sv)
    Sv_mask = create_default_noise_masks_oceanstream(source_Sv)
    assert Sv_mask["mask_false_seabed"].attrs["mask_type"] == "false_seabed"
    assert Sv_mask["mask_impulse"].attrs["parameters"] == ["thr=10", "m=5", "n=1"]
