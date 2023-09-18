"""
raw_reader.py
-------------
Module for reading, verifying, and converting echo sounder raw data files.

This module provides functionalities to:

- Search for raw echo sounder files within specified directories or paths.
- Verify the integrity of these files, ensuring they are readable by echopype.
- Extract essential metadata from the files, such as campaign ID,\
date of measurement, and sonar model.
- Convert raw files to specified formats (netCDF or zarr) and\
save them to a desired location.
- Group similar files based on specific criteria, such as campaign ID,\
sonar model, and time difference.

The module supports various sonar models including
EK60, ES70, EK80, EA640, AZFP, and AD2CP.
It also defines a time threshold for determining
the similarity between two consecutive files.

"""

# Import necessary libraries
import os
import re
from datetime import datetime, timedelta
from typing import Dict, List, Union

import echopype as ep

SUPPORTED_SONAR_MODELS = ["EK60", "ES70", "EK80", "EA640", "AZFP", "AD2CP"]
TIME_BETWEEN_FILES = 30  # time in minutes between two consecutive files


def file_finder(paths: Union[str, List[str]], file_type: str = "raw") -> List[str]:  # noqa: E501
    """
    Finds and returns all files of a specified type from given paths.

    This function searches for files of a specified type (e.g., "raw")
    within the provided paths.
    It can search within a single directory or
    across multiple specified file paths.

    Parameters:

    - paths (str or list[str]): If a string is provided,\
    it should be the absolute path to a directory.\
    If a list is provided,\
    it should contain absolute paths to individual files.
    - file_type (str, optional): The type of files to search for.\
    Defaults to "raw".

    Returns:

    - list[str]: A sorted list of all found files of the specified type.

    Raises:

    - ValueError: If the provided paths input is neither a directory\
    nor a list of file paths.

    Example:

     file_finder("/path/to/directory")
    ['/path/to/directory/file1.raw', '/path/to/directory/file2.raw']

     file_finder(["/path/to/file1.raw", "/path/to/file2.raw"])
    ['/path/to/file1.raw', '/path/to/file2.raw']
    """
    if isinstance(paths, str) and os.path.isdir(paths):
        ret_files = [
            os.path.join(paths, f_p)
            for f_p in os.listdir(paths)
            if os.path.isfile(os.path.join(paths, f_p))
        ]
        ret_files = file_finder(ret_files, file_type)
    elif isinstance(paths, list):
        ret_files = []
        for elem in paths:
            if "." + file_type in elem and os.path.isfile(elem):
                ret_files.append(elem)
    else:
        raise ValueError(
            "Invalid input. Provide either a directory\
             path or a list of file paths."
        )

    return sorted(ret_files)


def file_integrity_checking(
    file_path: str,
) -> Dict[str, Union[str, datetime, bool]]:  # noqa: E501
    """
    Checks the integrity of a given echo sounder file.

    This function verifies if the provided echo sounder file is
    readable by echopype and extracts
    essential metadata such as the campaign ID, date of measurement,
    and sonar model. The function
    supports raw, netCDF, and zarr file formats.

    Parameters:

    - file_path (str): Absolute path to the echo sounder file.

    Returns:

    - dict: A dictionary containing the following keys:
    'file_path': Absolute path to the file.
    'campaign_id': Identifier for the measuring\
    campaign extracted from the file name.
    'date': Date and time when the measurement started,\
     extracted from the file name.
    'sonar_model': Type of sonar that produced the file.
    'file_integrity': Boolean indicating if the file is readable by echopype.

    Raises:

    - Exception: If the file type is not supported or
    if there are issues reading the file.

    Example:

    file_integrity_checking("/path/to/JR161-D20230509-T100645.raw")
    {
    'file_path': '/path/to/JR161-D20230509-T100645.raw',
    'campaign_id': 'JR161',
    'date': datetime.datetime(2023, 5, 9, 10, 6, 45),
    'sonar_model': 'EK60',
    'file_integrity': True
    }
    """
    return_dict = {}
    # get file name from path
    file_name = os.path.split(file_path)[-1]
    # eliminate file type
    file_name = file_name.split(".")[0]
    campaign_id = file_name.split("-")[0]
    no_date_from_file_name = False
    date = datetime.now()
    try:
        pattern_date = r"D(\d{4})(\d{2})(\d{2})"
        pattern_time = r"T(\d{2})(\d{2})(\d{2})"

        matches_date = re.findall(pattern_date, file_name)[0]
        matches_time = re.findall(pattern_time, file_name)[0]

        year, month, day = matches_date
        hour, minute, second = matches_time

        datetime_string = f"D{year}{month}{day}-T{hour}{minute}{second}"
        date = datetime.strptime(datetime_string, "D%Y%m%d-T%H%M%S")
    except Exception as e:
        e += "!"
        no_date_from_file_name = True

    if ".raw" in file_path:
        for s_m in SUPPORTED_SONAR_MODELS:
            try:
                ed = ep.open_raw(file_path, sonar_model=s_m)  # type: ignore
                file_integrity = True
                break
            except ValueError:
                continue
        else:
            raise Exception("File type not supported for " + str(file_path))
    elif ".nc" or ".zarr" in file_path:
        try:
            ed = ep.open_converted(file_path)
            file_integrity = True
        except ValueError:
            raise Exception("File type not supported for " + str(file_path))
    else:
        raise Exception("File type not supported for " + str(file_path))
    if no_date_from_file_name:
        datetime_string = ed["Top-level"].date_created
        date = datetime.strptime(datetime_string, "%Y-%m-%dT%H:%M:%SZ")

    return_dict["file_path"] = file_path
    return_dict["campaign_id"] = campaign_id
    return_dict["date"] = date
    return_dict["sonar_model"] = ed.sonar_model
    return_dict["file_integrity"] = file_integrity
    return return_dict


def read_raw_files(file_dicts: List[Dict[str, Union[str, datetime, bool]]]) -> List[ep.EchoData]:
    """
    Reads multiple raw echo sounder files and returns a list of Datasets.

    This function processes a list of file information dictionaries,
    opens each raw file
    using the specified sonar model,
    and returns the corresponding datasets.

    Parameters:

    - file_dicts (list of dict): List of dictionaries, \
    each containing file information \
    as provided by the file_integrity_checking function.

    Returns:

    - list: List of EchoData datasets corresponding to each raw file.

    """
    ret_list = []
    for f_i in file_dicts:
        opened_file = _read_file(f_i["file_path"], f_i["sonar_model"])
        ret_list.append(opened_file)
    return ret_list


def read_processed_files(file_paths: List[str]) -> List[ep.EchoData]:
    """
    Reads multiple processed echo sounder files and returns a list of Datasets.

    This function processes a list of file paths, opens each processed file,
    and returns the corresponding datasets.

    Parameters:

    - file_paths (list of str): List of file paths\
    to processed echo sounder files.

    Returns:

    - list: List of EchoData datasets\
    corresponding to each processed file.

    """
    ret_list = []
    for file_path in file_paths:
        opened_file = _read_file(file_path)
        ret_list.append(opened_file)
    return ret_list


def _read_file(file_path: str, sonar_model: str = "EK80") -> ep.EchoData:
    """
    Reads an echo sounder file and
    returns the corresponding Dataset.

    This function determines the type of the file
     (raw, netCDF, or zarr) based on its
    extension and opens it using echopype.
    For raw files, the sonar model must be specified.

    Parameters:

    - file_path (str): Absolute path to the echo sounder file.
    - sonar_model (str, optional): Type of sonar model. Defaults to "EK80".\
      Relevant only for raw files.

    Returns:

    - EchoData: Dataset corresponding to the provided file.

    Raises:

    - Exception: If the file type is not supported by echopype.

    """
    file_name = os.path.split(file_path)[-1]
    if ".raw" in file_name:
        ed = ep.open_raw(file_path, sonar_model=sonar_model)  # type: ignore
    elif ".nc" in file_name or ".zarr" in file_name:
        ed = ep.open_converted(file_path)  # create an EchoData object
    else:
        raise Exception("File not supported by echopype.")
    return ed


def convert_raw_files(
    file_dicts: List[Dict[str, Union[str, datetime, bool]]],
    save_path: str = "",
    save_file_type: str = "nc",
) -> List[str]:
    """
    Converts multiple raw echo sounder files to the
    specified file type and saves them.

    This function processes a list of file information dictionaries,
    converts each raw file
    to the specified file type (netCDF or zarr),
    and saves the converted files to the given path.

    Parameters:

    - file_dicts (list of dict): List of dictionaries,\
    each containing file information.
    - save_path (str): Directory path where\
    the converted files will be saved.
    - save_file_type (str): Desired file type\
    for saving the converted files.\
    Options are 'nc' or 'zarr'.

    Returns:

    - list: List of paths to the saved converted files.

    """
    ret_list = []
    for f_i in file_dicts:
        opened_file = _read_file(f_i["file_path"], f_i["sonar_model"])
        _write_file(opened_file, save_path, save_file_type)
        file_name = os.path.split(f_i["file_path"])[-1]
        file_type = save_file_type
        new_file_name = file_name.replace("raw", file_type)
        ret_list.append(os.path.join(save_path, new_file_name))
    return ret_list


def _write_file(
    ed: ep.EchoData,
    save_path: str,
    save_file_type: str = "nc",
    overwrite: bool = False,  # noqa: E501
) -> str:
    """
    Writes an echo sounder dataset to a
    specified file type and saves it.

    This function takes an EchoData dataset,
    converts it to the specified file type
    (netCDF or zarr), and saves the file to the provided path.

    Parameters:

    - ed (EchoData): echo sounder dataset to be saved.
    - save_path (str): Directory path where the dataset will be saved.
    - save_file_type (str, optional): Desired file type\
    for saving the dataset. Defaults to 'nc'.\
      Options are 'nc' or 'zarr'.
    - overwrite (bool, optional): If True, overwrites\
    the file if it already exists. Defaults to False.

    Returns:

    - str: Path to the saved file.

    Raises:

    - Exception: If the specified file type is not supported by echopype.

    """
    if save_file_type == "nc":
        ed.to_netcdf(save_path=save_path, overwrite=overwrite)
    elif save_file_type == "zarr":
        ed.to_zarr(save_path=save_path, overwrite=overwrite)
    else:
        raise Exception("File type not supported echopype.")
    return save_path


def _is_similar(
    file_dict1: Dict[str, Union[str, datetime, bool]],
    file_dict2: Dict[str, Union[str, datetime, bool]],
) -> bool:
    """
    Determines if two file information dictionaries
    are similar based on specific criteria.

    This function checks if two file dictionaries
    have the same campaign ID, sonar model,
    file integrity, and if their date difference
    is within a specified time range.

    Parameters:

    - file_dict1 (dict): First file information dictionary.
    - file_dict2 (dict): Second file information dictionary.

    Returns:

    - bool: True if the file dictionaries are similar\
    based on the criteria, False otherwise.

    """
    if file_dict1["campaign_id"] != file_dict2["campaign_id"]:
        return False
    if file_dict1["sonar_model"] != file_dict2["sonar_model"]:
        return False
    if file_dict1["file_integrity"] != file_dict2["file_integrity"]:
        return False
    date_diff = file_dict1["date"] - file_dict2["date"]
    if date_diff > timedelta(minutes=TIME_BETWEEN_FILES):
        return False
    return True


def split_files(
    file_dicts: List[Dict[str, Union[str, datetime, bool]]]
) -> List[List[Dict[str, Union[str, datetime, bool]]]]:
    """
    Splits a list of file information dictionaries
    into sublists based on their similarity.

    This function processes a list of file information
    dictionaries and groups them into
    sublists where each sublist contains files
    that are similar to each other based on
    specific criteria.

    Parameters:

    - file_dicts (list of dict): List of file information dictionaries.

    Returns:

    - list of lists: List containing sublists of file dictionaries\
    grouped by their similarity.

    """
    list_of_lists = []

    temp_list = []
    prev_elem = file_dicts[0]
    for elem in file_dicts:
        if _is_similar(elem, prev_elem):
            temp_list.append(elem)
        else:
            list_of_lists.append(temp_list)
            temp_list = [elem]
        prev_elem = elem
    list_of_lists.append(temp_list)
    return list_of_lists


def concatenate_files(file_dicts: List[Dict[str, Union[str, datetime, bool]]]) -> ep.EchoData:
    list_of_datasets = []
    for file_info in file_dicts:
        list_of_datasets.append(_read_file(file_info["file_path"]))
    combined_dataset = ep.combine_echodata(list_of_datasets)
    return combined_dataset
