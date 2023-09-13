import os
from ftplib import FTP

import pytest

from oceanstream.L0_unprocessed_data.raw_reader import (
    concatenate_files,
    convert_raw_files,
    file_finder,
    file_integrity_checking,
    read_processed_files,
    read_raw_files,
    split_files,
)

current_directory = os.path.dirname(os.path.abspath(__file__))
TEST_DATA_FOLDER = os.path.join(current_directory, "..", "test_data", "ek60")


def test_file_finder(ftp_data):
    # Test with a valid directory path containing files
    found_files = file_finder(ftp_data)
    assert (
        len(found_files) > 0
    )  # Assuming there's at least one file in the FTP directory
    assert all([os.path.isfile(f) for f in found_files])

    # Test with a list of valid file paths
    assert file_finder(found_files, "raw") == found_files

    # Test with a directory containing no files of the specified type
    # Assuming there are no ".txt" files in the FTP directory
    assert file_finder(ftp_data, "txt") == []

    # Test with a list containing invalid file paths
    invalid_path = os.path.join(ftp_data, "invalid_file.raw")
    assert file_finder([found_files[0], invalid_path], "raw") == [found_files[0]]

    # Test with an invalid path (neither directory nor list of file paths)
    with pytest.raises(ValueError):
        file_finder(12345)


def test_file_integrity_checking(ftp_data):
    found_files = file_finder(ftp_data)
    # Test with a valid raw echo sounder file
    result_files = file_integrity_checking(found_files[0])
    assert result_files["file_integrity"] == True
    assert result_files["sonar_model"] in [
        "EK60",
        "ES70",
        "EK80",
        "EA640",
        "AZFP",
        "AD2CP",
    ]

    # Test with a valid netCDF file
    valid_netcdf_file = convert_raw_files(
        [result_files], save_path=TEST_DATA_FOLDER, save_file_type="nc"
    )[0]
    result = file_integrity_checking(valid_netcdf_file)
    assert result["file_integrity"] == True

    # Test with a valid zarr file
    valid_zarr_file = convert_raw_files(
        [result_files], save_path=TEST_DATA_FOLDER, save_file_type="zarr"
    )[0]
    result = file_integrity_checking(valid_zarr_file)
    assert result["file_integrity"] == True

    # Test with an unsupported file type
    unsupported_file = file_finder(ftp_data, "png")[0]
    with pytest.raises(Exception, match="File type not supported"):
        file_integrity_checking(unsupported_file)


def test_read_raw_files(ftp_data):
    # Test with a list of valid file dictionaries
    found_files = file_finder(ftp_data, "raw")
    file_dicts = [file_integrity_checking(f) for f in found_files]

    datasets = read_raw_files(file_dicts)
    assert len(datasets) == 17
    # Additional assertions can be added based on expected dataset properties

    # Test with an empty list
    datasets = read_raw_files([])
    assert len(datasets) == 0


def test_read_processed_files(ftp_data):
    # Test with a list of valid processed file paths
    found_files = file_finder(ftp_data, "raw")
    file_dicts = [file_integrity_checking(f) for f in found_files[:3]]
    file_paths = convert_raw_files(
        file_dicts, save_path=TEST_DATA_FOLDER, save_file_type="nc"
    )

    datasets = read_processed_files(file_paths)
    assert len(datasets) == 3
    # Additional assertions can be added based on expected dataset properties

    # Test with an empty list
    datasets = read_processed_files([])
    assert len(datasets) == 0


def test_convert_raw_files(ftp_data):
    # Test conversion of raw files to netCDF
    found_files = file_finder(ftp_data, "raw")
    file_dicts = [file_integrity_checking(f) for f in found_files[:3]]
    converted_files = convert_raw_files(
        file_dicts, save_path=TEST_DATA_FOLDER, save_file_type="nc"
    )
    for file in converted_files:
        assert os.path.exists(file)
        assert file.endswith(".nc")

    # Test conversion of raw files to zarr
    converted_files = convert_raw_files(
        file_dicts, save_path=TEST_DATA_FOLDER, save_file_type="zarr"
    )
    for file in converted_files:
        assert os.path.exists(file)
        assert file.endswith(".zarr")

    # Test with an unsupported save file type
    with pytest.raises(
        Exception
    ):  # Assuming the function raises an exception for unsupported file types
        convert_raw_files(
            file_dicts, save_path=TEST_DATA_FOLDER, save_file_type="unsupported"
        )

    # Test with an empty save path
    converted_files = convert_raw_files(file_dicts, save_file_type="nc")
    for file in converted_files:
        assert os.path.exists(file)
        assert file.endswith(".nc")


def test_split_files(ftp_data):
    # Test with a list of similar file dictionaries
    found_files = file_finder(ftp_data, "raw")
    file_dicts = [file_integrity_checking(f) for f in found_files[5:7]]

    grouped_files = split_files(file_dicts)
    assert len(grouped_files) == 1
    assert len(grouped_files[0]) == 2

    # Test with a list of dissimilar file dictionaries
    found_files = file_finder(ftp_data, "raw")
    file_dicts = [file_integrity_checking(f) for f in found_files[:3]]
    grouped_files = split_files(file_dicts)
    assert len(grouped_files) == 3
    assert len(grouped_files[0]) == 1
    assert len(grouped_files[1]) == 1

    # Test with an empty list
    with pytest.raises(Exception):
        grouped_files = split_files([])


def test_concatenate_files(ftp_data):
    # Test with a list of valid file dictionaries
    found_files = file_finder(ftp_data, "raw")
    file_dicts = [file_integrity_checking(f) for f in found_files[5:7]]
    converted_files = convert_raw_files(
        file_dicts, save_path=TEST_DATA_FOLDER, save_file_type="nc"
    )
    file_dicts = [file_integrity_checking(f) for f in converted_files]
    concatenated_dataset = concatenate_files(file_dicts)
    # Here, you might want to add more assertions based on the expected properties of the concatenated dataset
    assert concatenated_dataset is not None
