import re
from pathlib import Path

import pytest
import xarray as xr

from oceanstream.L2_calibrated_data.processed_data_io import write_processed
from tests.conftest import TEST_DATA_FOLDER


def test_write_processed_nc(enriched_ek60_Sv):
    enriched_sv = enriched_ek60_Sv

    # Define the file path and name
    file_path = (
        TEST_DATA_FOLDER  # Using pytest's TEST_DATA_FOLDER fixture to get a temporary directory
    )
    file_name = "test_dataset_Sv.nc"

    # Use the function to save the dataset
    write_processed(enriched_sv, file_path, file_name)

    # Read the saved dataset back
    saved_dataset_path = Path(file_path) / file_name
    loaded_dataset = xr.open_dataset(saved_dataset_path)

    # Assert that the loaded dataset matches the original dataset
    xr.testing.assert_equal(loaded_dataset, enriched_sv)

    file_name = "test_dataset_Sv_enriched.zarr"

    # Use the function to save the dataset
    write_processed(enriched_sv, file_path, file_name)

    # Read the saved dataset back
    saved_dataset_path = Path(file_path) / file_name
    loaded_dataset = xr.open_zarr(saved_dataset_path)

    # Assert that the loaded dataset matches the original dataset
    xr.testing.assert_equal(loaded_dataset, enriched_sv)


def test_write_processed_overwrite_behavior(enriched_ek60_Sv):
    sv_echopype_ek60 = enriched_ek60_Sv

    # Define the file path and name
    file_path = TEST_DATA_FOLDER
    file_name = "overwrite_test_dataset_Sv.nc"

    # Use the function to save the dataset
    write_processed(sv_echopype_ek60, file_path, file_name)

    # Modify the dataset
    modified_sv = sv_echopype_ek60.copy()
    modified_sv.attrs["test_attribute"] = "This is a test modification"

    # Try saving the modified dataset with overwrite=False
    write_processed(modified_sv, file_path, file_name, overwrite=False)

    # Read the saved dataset back
    saved_dataset_path = Path(file_path) / file_name
    loaded_dataset = xr.open_dataset(saved_dataset_path)

    # Assert that the loaded dataset matches the original dataset (and not the modified one)
    xr.testing.assert_equal(loaded_dataset, sv_echopype_ek60)
    assert "test_attribute" not in loaded_dataset.attrs
    loaded_dataset.close()
    # Save the modified dataset with overwrite=True
    write_processed(modified_sv, file_path, file_name, overwrite=True)

    # Read the saved dataset back
    loaded_dataset = xr.open_dataset(saved_dataset_path)

    # Assert that the loaded dataset matches the modified dataset
    xr.testing.assert_equal(loaded_dataset, modified_sv)
    assert loaded_dataset.attrs["test_attribute"] == "This is a test modification"
    loaded_dataset.close()


def test_invalid_dataset_input():
    invalid_input = "This is not a dataset"
    file_path = TEST_DATA_FOLDER
    file_name = "invalid_input_test.nc"
    with pytest.raises(TypeError, match="Expected a xarray Dataset"):
        write_processed(invalid_input, file_path, file_name)


# def test_invalid_directory_path(enriched_ek60_Sv):
#     sv_echopype_ek60 = enriched_ek60_Sv
#     # Use pathlib to create the path
#     invalid_path = Path("/path/that/does/not/exist")
#     file_name = "invalid_path_test.nc"
#
#     path_pattern = re.escape(str(invalid_path))
#     with pytest.raises(FileNotFoundError, match=f"Invalid path provided: {path_pattern}"):
#         write_processed(sv_echopype_ek60, invalid_path, file_name)


def test_unsupported_file_type(enriched_ek60_Sv):
    sv_echopype_ek60 = enriched_ek60_Sv
    file_path = TEST_DATA_FOLDER
    file_name = "unsupported_file_type_test.txt"
    with pytest.raises(
        ValueError,
        match="File name provided has unsupported format: unsupported_file_type_test.txt",
    ):
        write_processed(sv_echopype_ek60, file_path, file_name)


def test_unsupported_file_name_format(enriched_ek60_Sv):
    sv_echopype_ek60 = enriched_ek60_Sv
    file_path = TEST_DATA_FOLDER
    file_name = "unsupported.file.name.format.nc"
    with pytest.raises(
        ValueError,
        match="File name provided has unsupported format: unsupported.file.name.format.nc",
    ):
        write_processed(sv_echopype_ek60, file_path, file_name)


def test_default_file_name(enriched_ek60_Sv):
    sv_echopype_ek60 = enriched_ek60_Sv
    default_name = Path(sv_echopype_ek60.source_filenames[0].values.item()).stem + ".nc"
    default_path = Path(TEST_DATA_FOLDER) / default_name

    # If the file already exists, remove it to ensure a fresh test
    if default_path.exists():
        default_path.unlink()

    write_processed(sv_echopype_ek60, TEST_DATA_FOLDER)

    assert default_path.exists(), "Default file name not used when no file_name is provided."
    default_path.unlink()  # Cleanup after test


def test_append_file_suffix(enriched_ek60_Sv):
    sv_echopype_ek60 = enriched_ek60_Sv
    file_name_without_suffix = "test_file"
    expected_file_path = Path(TEST_DATA_FOLDER) / (file_name_without_suffix + ".nc")

    # If the file already exists, remove it to ensure a fresh test
    if expected_file_path.exists():
        expected_file_path.unlink()

    write_processed(sv_echopype_ek60, TEST_DATA_FOLDER, file_name_without_suffix)

    assert expected_file_path.exists(), "File suffix not appended correctly."
    expected_file_path.unlink()  # Cleanup after test


def test_file_content_verification(enriched_ek60_Sv):
    sv_echopype_ek60 = enriched_ek60_Sv
    file_name = "content_verification_test.nc"
    file_path = Path(TEST_DATA_FOLDER) / file_name

    write_processed(sv_echopype_ek60, TEST_DATA_FOLDER, file_name)

    loaded_dataset = xr.open_dataset(file_path)
    xr.testing.assert_equal(loaded_dataset, sv_echopype_ek60)
    loaded_dataset.close()
    file_path.unlink()  # Cleanup after test
