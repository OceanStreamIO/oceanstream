from oceanstream.L2_calibrated_data.noise_masks import (
    add_metadata_to_mask,
    attach_mask_to_dataset,
    create_attenuation_mask,
    create_default_noise_masks_oceanstream,
    create_impulse_mask,
    create_noise_masks_rapidkrill,
    create_seabed_mask,
    create_transient_mask,
    dict_to_formatted_list,
)
from oceanstream.L2_calibrated_data.sv_computation import compute_sv


def test_impulse(ed_ek_60_for_Sv):
    source_Sv = compute_sv(ed_ek_60_for_Sv)
    RYAN_DEFAULT_PARAMS = {"thr": 10, "m": 5, "n": 1}
    mask = create_impulse_mask(source_Sv, parameters=RYAN_DEFAULT_PARAMS)
    assert mask["channel"].shape == (3,)


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


def test_mask_metadata(ed_ek_60_for_Sv, metadata=None):
    if metadata is None:
        metadata = {"test": "test"}
    source_Sv = compute_sv(ed_ek_60_for_Sv)
    mask = create_seabed_mask(source_Sv)
    mask_with_metadata = add_metadata_to_mask(mask, metadata)
    for k, v in metadata.items():
        assert mask_with_metadata.attrs[k] == v


def test_add_mask(ed_ek_60_for_Sv, metadata=None):
    if metadata is None:
        metadata = {"mask_type": "seabed"}
    source_Sv = compute_sv(ed_ek_60_for_Sv)
    mask = create_seabed_mask(source_Sv)
    add_metadata_to_mask(mask, metadata)
    Sv_mask = attach_mask_to_dataset(source_Sv, mask)
    for k, v in metadata.items():
        assert Sv_mask["mask_seabed"].attrs[k] == v
    assert Sv_mask["mask_seabed"].attrs["mask_type"]


def test_add_masks_rapidkrill(ed_ek_60_for_Sv):
    source_Sv = compute_sv(ed_ek_60_for_Sv)
    Sv_mask = create_noise_masks_rapidkrill(source_Sv)
    assert Sv_mask["mask_seabed"].attrs["mask_type"] == "seabed"


def test_dict_to_formatted_list():
    # Define a sample dictionary
    sample_dict = {
        "m": 5,
        "n": 20,
        "operation": "percentile15",
    }

    # Expected output
    expected_output = ["m=5", "n=20", "operation=percentile15"]

    # Call the function
    result = dict_to_formatted_list(sample_dict)

    # Assert that the result matches the expected output
    assert result == expected_output


def test_add_masks_default_oceanstream(ed_ek_60_for_Sv):
    source_Sv = compute_sv(ed_ek_60_for_Sv)
    Sv_mask = create_default_noise_masks_oceanstream(source_Sv)
    assert Sv_mask["mask_false_seabed"].attrs["mask_type"] == "false_seabed"
    assert Sv_mask["mask_impulse"].attrs["parameters"] == ["thr=10", "m=5", "n=1"]
