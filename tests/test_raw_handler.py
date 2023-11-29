import os
import urllib.request
import pytest

from oceanstream.L0_unprocessed_data.raw_handler import (
    convert_raw_files,
    file_finder,
    file_integrity_checking,
    read_processed_files,
    read_raw_files,
    split_files,
    detect_sonar_model,
)
from tests.conftest import TEST_DATA_FOLDER


def test_file_finder(ftp_data):
    # Test with a valid directory path containing files
    found_files = file_finder(ftp_data)
    assert len(found_files) > 0  # Assuming there's at least one file in the FTP directory
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
    assert result_files["campaign_id"] == 'SignytoP2'

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
    assert len(datasets) == 16
    # Additional assertions can be added based on expected dataset properties

    # Test with an empty list
    datasets = read_raw_files([])
    assert len(datasets) == 0


def test_read_processed_files(ftp_data):
    # Test with a list of valid processed file paths
    found_files = file_finder(ftp_data, "raw")
    file_dicts = [file_integrity_checking(f) for f in found_files[:3]]
    file_paths = convert_raw_files(file_dicts, save_path=TEST_DATA_FOLDER, save_file_type="nc")

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
    converted_files = convert_raw_files(file_dicts, save_path=TEST_DATA_FOLDER, save_file_type="nc")
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
        convert_raw_files(file_dicts, save_path=TEST_DATA_FOLDER, save_file_type="unsupported")

    # Test with an empty save path
    converted_files = convert_raw_files(file_dicts, save_file_type="nc")
    for file in converted_files:
        assert os.path.exists(file)
        assert file.endswith(".nc")
        os.remove(file)


def test_split_files(ftp_data):
    # Test with a list of similar file dictionaries
    found_files = file_finder(ftp_data, "raw")
    file_dicts = [file_integrity_checking(f) for f in found_files[5:7]]

    grouped_files = split_files(file_dicts)
    assert len(grouped_files) == 2
    assert len(grouped_files[0]) == 1

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


def test_detect_sonar_model_ek60(ftp_data):
    # Test with a valid raw echo sounder file
    found_files = file_finder(ftp_data, "raw")
    sonar_model = detect_sonar_model(found_files[0])

    assert sonar_model == "EK60"


def test_detect_sonar_model_ek80(ftp_data):
    base_url = "https://noaa-wcsd-pds.s3.amazonaws.com/"
    path = "data/raw/Sally_Ride/SR1611/EK80/"
    file_name = "D20161108-T214612.raw"

    local_path = os.path.join(TEST_DATA_FOLDER, file_name)
    if not os.path.isfile(local_path):
        raw_file_address = base_url + path + file_name
        urllib.request.urlretrieve(raw_file_address, local_path)

    sonar_model = detect_sonar_model(local_path)

    assert sonar_model == "EK80"
