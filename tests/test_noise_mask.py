from oceanstream.denoise.noise_masks import OCEANSTREAM_MASK_PARAMETERS
from oceanstream.denoise.noise_masks import (
    create_attenuation_mask,
    create_impulse_mask,
    create_seabed_mask,
    create_transient_mask,
    create_multiple_masks,
)

TEST_MASK_PARAMETERS = {
    "transient": {
        "method": "ryan",
        "params": {
            "m": 5,
            "n": 5,
            "thr": 20,
            "excludeabove": 250,
            "dask_chunking": {"ping_time": 100},
            "operation": "mean",
        },
    },
    "attenuation": {
        "method": "ryan",
        "params": {
            "r0": 180,
            "r1": 280,
            "n": 5,
            "m": None,
            "thr": -5,
            "start": 0,
            "offset": 0,
        },
    },
    "impulse": {"method": "ryan", "params": {"thr": 3, "m": 3, "n": 1}},
    "seabed": {
        "method": "ariza",
        "params": {
            "r0": 10,
            "r1": 1000,
            "roff": 0,
            "thr": -40,
            "ec": 1,
            "ek": (1, 3),
            "dc": 10,
            "dk": (3, 7),
        },
    },
    "false_seabed": {
        "method": "blackwell",
        "params": {
            "theta": None,
            "phi": None,
            "r0": 10,
            "r1": 1000,
            "tSv": -75,
            "ttheta": 702,
            "tphi": 282,
            "wtheta": 28,
            "wphi": 52,
        },
    },
}

def test_impulse(enriched_ek60_Sv):
    source_Sv = enriched_ek60_Sv
    RYAN_DEFAULT_PARAMS = OCEANSTREAM_MASK_PARAMETERS["impulse"]["params"]
    mask = create_impulse_mask(source_Sv, parameters=RYAN_DEFAULT_PARAMS)
    assert mask["channel"].shape == (3,)


def test_transient(enriched_ek60_Sv):
    source_Sv = enriched_ek60_Sv
    RYAN_DEFAULT_PARAMS = OCEANSTREAM_MASK_PARAMETERS["transient"]["params"]
    mask_ryan = create_transient_mask(
        source_Sv, parameters=RYAN_DEFAULT_PARAMS, method="fielding"
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
    Sv_mask = create_multiple_masks(enriched_Sv, TEST_MASK_PARAMETERS)
    assert Sv_mask["mask_seabed"].attrs["mask_type"] == "seabed"
    assert Sv_mask["mask_impulse"].attrs["parameters"] == ["thr=3", "m=3", "n=1"]

