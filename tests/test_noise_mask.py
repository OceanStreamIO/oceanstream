import pytest
from oceanstream.L2_calibrated_data.noise_masks import OCEANSTREAM_MASK_PARAMETERS

from oceanstream.L2_calibrated_data.noise_masks import (
    create_attenuation_mask,
    # create_default_noise_masks_oceanstream,
    create_impulse_mask,
    # create_noise_masks_rapidkrill,
    create_seabed_mask,
    create_transient_mask,
    create_multiple_masks,
)


def test_impulse(enriched_ek60_Sv):
    source_Sv = enriched_ek60_Sv
    RYAN_DEFAULT_PARAMS = OCEANSTREAM_MASK_PARAMETERS["impulse"]["params"]
    mask = create_impulse_mask(source_Sv, parameters=RYAN_DEFAULT_PARAMS)
    assert mask["channel"].shape == (3,)


def test_transient(enriched_ek60_Sv):
    source_Sv = enriched_ek60_Sv
    RYAN_DEFAULT_PARAMS = OCEANSTREAM_MASK_PARAMETERS["transient"]["params"]
    mask_ryan = create_transient_mask(
        source_Sv, parameters=RYAN_DEFAULT_PARAMS, method="ryan"
    )
    assert mask_ryan["channel"].shape == (3,)


def test_attenuation(enriched_ek60_Sv):
    DEFAULT_RYAN_PARAMS = OCEANSTREAM_MASK_PARAMETERS["attenuation"]["params"]
    source_Sv = enriched_ek60_Sv
    mask = create_attenuation_mask(source_Sv, parameters=DEFAULT_RYAN_PARAMS)
    assert mask["channel"].shape == (3,)


def test_seabed(enriched_ek60_Sv):
    ARIZA_DEFAULT_PARAMS = OCEANSTREAM_MASK_PARAMETERS["seabed"]["params"]
    source_Sv = enriched_ek60_Sv
    mask = create_seabed_mask(
        source_Sv,
        method="ariza",
        parameters=ARIZA_DEFAULT_PARAMS,
    )
    assert mask["channel"].shape == (3,)


def test_create_masks(enriched_ek60_Sv):
    enriched_Sv = enriched_ek60_Sv
    Sv_mask = create_multiple_masks(enriched_Sv)
    assert Sv_mask["mask_seabed"].attrs["mask_type"] == "seabed"
    assert Sv_mask["mask_impulse"].attrs["parameters"] == ["thr=3", "m=3", "n=1"]

