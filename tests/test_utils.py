import os

from oceanstream.denoise.noise_masks import create_seabed_mask
from oceanstream.echodata.sv_computation import compute_sv
from oceanstream.exports.plot import plot_all_channels
from oceanstream.utils import *

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

    ARIZA_DEFAULT_PARAMS = {
        "r0": 10,
        "r1": 1000,
        "roff": 0,
        "thr": -40,
        "ec": 1,
        "ek": (1, 3),
        "dc": 10,
        "dk": (3, 7),
    }
    mask = create_seabed_mask(
        source_Sv,
        method="ariza",
        parameters=ARIZA_DEFAULT_PARAMS,
    )
    mask_with_metadata = add_metadata_to_mask(mask, metadata)
    for k, v in metadata.items():
        assert mask_with_metadata.attrs[k] == v


def test_add_mask(ed_ek_60_for_Sv, metadata=None):
    if metadata is None:
        metadata = {"mask_type": "seabed"}
    source_Sv = compute_sv(ed_ek_60_for_Sv)
    ARIZA_DEFAULT_PARAMS = {
        "r0": 10,
        "r1": 1000,
        "roff": 0,
        "thr": -40,
        "ec": 1,
        "ek": (1, 3),
        "dc": 10,
        "dk": (3, 7),
    }
    mask = create_seabed_mask(
        source_Sv,
        method="ariza",
        parameters=ARIZA_DEFAULT_PARAMS,
    )
    add_metadata_to_mask(mask, metadata)
    Sv_mask = attach_mask_to_dataset(source_Sv, mask)
    for k, v in metadata.items():
        assert Sv_mask["mask_seabed"].attrs[k] == v
    assert Sv_mask["mask_seabed"].attrs["mask_type"]


def test_tfc():
    data = xr.DataArray(
        data=[True, False, True],
        dims=["x"],
        coords={"x": [1, 2, 3]}
    )
    res = tfc(data)
    assert res == (2, 1)


def test_plotting(ed_ek_60_for_Sv):
    current_directory = os.path.dirname(os.path.abspath(__file__))
    TEST_DATA_FOLDER = os.path.join(current_directory, "..", "test_data")
    source_Sv = compute_sv(ed_ek_60_for_Sv)
    plot_all_channels(source_Sv,name="test_image", save_path=TEST_DATA_FOLDER)

    plot_all_channels(source_Sv,source_Sv, name="test_image_double", save_path=TEST_DATA_FOLDER)

