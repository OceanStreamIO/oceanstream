from oceanstream.L2_calibrated_data.noise_masks import create_seabed_mask
from oceanstream.L2_calibrated_data.sv_computation import compute_sv
from oceanstream.utils import add_metadata_to_mask, attach_mask_to_dataset, dict_to_formatted_list


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
