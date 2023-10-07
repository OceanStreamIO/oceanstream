from oceanstream.L2_calibrated_data.noise_masks import (
    create_attenuation_mask,
    create_impulse_mask,
    create_noise_masks_rapidkrill,
    create_seabed_mask,
    create_transient_mask,
    add_metadata_to_mask,
    attach_mask_to_dataset,
)


def test_impulse(sv_dataset_jr230):
    source_Sv = sv_dataset_jr230
    RYAN_DEFAULT_PARAMS = {"thr": 10, "m": 5, "n": 1}
    mask = create_impulse_mask(source_Sv, parameters=RYAN_DEFAULT_PARAMS)
    assert mask["channel"].shape == (3,)


def test_transient(sv_dataset_jr161):
    source_Sv = sv_dataset_jr161
    RYAN_DEFAULT_PARAMS = {
        "m": 5,
        "n": 20,
        "thr": 20,
        "excludeabove": 250,
        "operation": "percentile15",
    }
    FIELDING_DEFAULT_PARAMS = {
        "r0": 200,
        "r1": 1000,
        "n": 20,
        "thr": [2, 0],
        "roff": 250,
        "jumps": 5,
        "maxts": -35,
        "start": 0,
    }
    mask_fielding = create_transient_mask(source_Sv, parameters=FIELDING_DEFAULT_PARAMS, method="fielding")
    assert mask_fielding["channel"].shape == (3,)
    mask_ryan = create_transient_mask(source_Sv, parameters=RYAN_DEFAULT_PARAMS, method="ryan")
    assert mask_ryan["channel"].shape == (3,)


def test_attenuation(sv_dataset_jr161):
    DEFAULT_RYAN_PARAMS = {"r0": 180, "r1": 280, "n": 30, "thr": -6, "start": 0}
    source_Sv = sv_dataset_jr161
    mask = create_attenuation_mask(source_Sv, parameters=DEFAULT_RYAN_PARAMS)
    assert mask["channel"].shape == (3,)


def test_seabed(complete_dataset_jr179):
    source_Sv = complete_dataset_jr179
    mask = create_seabed_mask(source_Sv)
    assert mask["channel"].shape == (3,)


def test_mask_metadata(complete_dataset_jr179, metadata=None):
    if metadata is None:
        metadata = {"test": "test"}
    source_Sv = complete_dataset_jr179
    mask = create_seabed_mask(source_Sv)
    mask_with_metadata = add_metadata_to_mask(mask, metadata)
    for k, v in metadata.items():
        assert mask_with_metadata.attrs[k] == v


def test_add_mask(complete_dataset_jr179, metadata=None):
    if metadata is None:
        metadata = {"mask_type": "seabed"}
    source_Sv = complete_dataset_jr179
    mask = create_seabed_mask(source_Sv)
    add_metadata_to_mask(mask, metadata)
    Sv_mask = attach_mask_to_dataset(source_Sv, mask)
    for k, v in metadata.items():
        assert Sv_mask["mask_seabed"].attrs[k] == v
    assert Sv_mask["mask_seabed"].attrs["mask_type"]


def test_add_masks_rapidkrill(complete_dataset_jr179):
    source_Sv = complete_dataset_jr179
    Sv_mask = create_noise_masks_rapidkrill(source_Sv)
    assert Sv_mask["mask_seabed"].attrs["mask_type"] == "seabed"
