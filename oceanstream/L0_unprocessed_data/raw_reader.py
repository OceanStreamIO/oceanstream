"""
Module Name: raw_reader.py
Description: The raw reader reads multiple raw data files,
regardless of their source, and concatenates them
into a unified dataset if possible.
Author: Mihai Boldeanu
Date: 09/05/2023
"""

# Import necessary libraries
import os
from datetime import datetime, timedelta

import echopype as ep

SUPPORTED_SONAR_MODELS = ["EK60", "ES70", "EK80", "EA640", "AZFP", "AD2CP"]
TIME_BETWEEN_FILES = 30  # time in minutes between two consecutive files


def file_finder(paths, file_type="raw"):
    """
    This function finds all the raw echosounder files.

    Parameters:
    - paths (str or list(str)): paths should be a list of absolute paths
    to files or a path to the dir containing files.

    Returns:
    - files: All the raw files in the folder

    Example:
    file_finder(paths)
    Expected Output
    all the raw files in that path
    """
    if isinstance(paths, str) and os.path.isdir(paths):
        files = [
            os.path.join(paths, file)
            for file in os.listdir(paths)
            if os.path.isfile(os.path.join(paths, file))
        ]
        files = file_finder(files)
    elif isinstance(paths, list):
        files = []
        for elem in paths:
            if "." + file_type in elem and os.path.isfile(elem):
                files.append(elem)
    else:
        raise ValueError(
            "Invalid input. Provide either a directory\
             path or a list of file paths."
        )

    return sorted(files)


def file_integrity_checking(file_path):
    """
    This functions checks the time range of one file and
    if it could be appended into a Dataset.

    Parameters:
    - file_path (str): file should be an absolute path
    to a raw file.

    Returns:
    - return_dict: contains:
        - file_path: abs path to the file
        - campaign_id: measuring campaign id
        - date: the date for the start of the file measurement
        - sonar_model: the type of sonar that produced the file
        - file_integrity: if the raw file is readable with echopype


    Example:
    file_checking(paths)
    Expected Output
    """
    return_dict = {}
    # get file name from path
    file_name = os.path.split(file_path)[-1]
    # eliminate file type
    file_name = file_name.split(".")[0]
    campaign_id = file_name.split("-")[0]
    date_string = file_name.split("-")[1] + "-" + file_name.split("-")[2]
    date = datetime.strptime(date_string, "D%Y%m%d-T%H%M%S")
    file_integrity = False
    if ".raw" in file_path:
        for sonar_model in SUPPORTED_SONAR_MODELS:
            try:
                ed = ep.open_raw(file_path, sonar_model=sonar_model)
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

    return_dict["file_path"] = file_path
    return_dict["campaign_id"] = campaign_id
    return_dict["date"] = date
    return_dict["sonar_model"] = ed.sonar_model
    return_dict["file_integrity"] = file_integrity
    return return_dict


def read_raw_files(file_dicts):
    """
    This functions reads multiple files that have been
     checked and returns a Dataset list.

    Parameters:
    - file_dicts (dict): dictionary has all
    info provided by file_integrity_checking
    function

    Returns:
    - Dataset: the open data set list

    """
    ret_list = []
    for f_i in file_dicts:
        opened_file = _read_file(f_i["file_path"], f_i["sonar_model"])
        ret_list.append(opened_file)
    return ret_list


def read_processed_files(file_paths):
    """
    This functions reads multiple files that have been
     checked and returns a Dataset list.

    Parameters:
    - file_paths (dict): dictionary has all info
    provided by file_integrity_checking
    function

    Returns:
    - Dataset: the open data set list

    """
    ret_list = []
    for file_path in file_paths:
        opened_file = _read_file(file_path)
        ret_list.append(opened_file)
    return ret_list


def _read_file(file_path, sonar_model="EK80"):
    """
    This functions reads a file that has been
    checked and returns a Dataset.

    Parameters:
    - file_dict (dict): dictionary has all info provided
    by file_integrity_checking function

    Returns:
    - Dataset: the open data set

    """
    file_name = os.path.split(file_path)[-1]
    if ".raw" in file_name:
        ed = ep.open_raw(file_path, sonar_model=sonar_model)
    elif ".nc" in file_name or ".zarr" in file_name:
        ed = ep.open_converted(file_path)  # create an EchoData object
    else:
        raise Exception("File not supported by echopype.")
    return ed


def convert_raw_files(file_dicts, save_path="", save_file_type="nc"):
    """
    This functions reads multiple files that have been
     checked and returns a Dataset list.

    Parameters:
    - file_dicts (dict): list of the file infos
    - save_path: path to save the converted files
    - save_file_type: file type nc or zarr

    Returns:
    - Dataset: the open data set list

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


def _write_file(ed, save_path, save_file_type="nc", overwrite=False):
    """
    This functions reads a file that has been checked and returns a Dataset.

    Parameters:
    - Echopype Dataset: a dataset with data from raw/transformed file
    - save_path: a path to the save directory for transformed files

    Returns:
    - file_path: location where the file was saved

    """
    if save_file_type == "nc":
        ed.to_netcdf(save_path=save_path, overwrite=overwrite)
    elif save_file_type == "zarr":
        ed.to_zarr(save_path=save_path, overwrite=overwrite)
    else:
        raise Exception("File type not supported echopype.")
    return save_path


def _is_similar(file_dict1, file_dict2):
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


def split_files(file_dicts):
    """
    This functions reads a file that has been checked and returns a Dataset.

    Parameters:
    - file_dicts: list of the file info for
    either raw or converted files

    Returns:
    - list_of_lists: splits continuous data into lists

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

    return list_of_lists


# Additional functions...


if __name__ == "__main__":
    # Code to be executed if this module is run as a standalone script
    # For example, for testing purposes

    # Get list of files
    path = r"C:\Users\mishu\OneDrive\Desktop\pinelab\test_data\ek60"
    files = file_finder(path)
    files = [
        "JR161-D20061118-T010645.raw",
        "JR161-D20061127-T115759.raw",
        "JR161-D20061127-T144557.raw",
        "JR177-D20080122-T151230.raw",
        "JR177-D20080206-T100028.raw",
        "JR177-D20080206-T101423.raw",
        "JR177-D20080206-T124742.raw",
        "JR177-D20080214-T220433.raw",
        "JR179-D20080410-T133235.raw",
        "JR179-D20080410-T142619.raw",
        "JR179-D20080410-T143945.raw",
        "JR179-D20080410-T145311.raw",
        "JR179-D20080410-T150637.raw",
        "JR230-D20091215-T121917.raw",
        "JR245-D20110116-T182142.raw",
        "JR245-D20110117-T213756.raw",
    ]
    files = [os.path.join(path, f) for f in files]
    files = file_finder(files, "raw")
    # Check to be raw files integrity
    raw_files_info = []
    for file in files:
        file_info = file_integrity_checking(file)
        if file_info["file_integrity"]:
            raw_files_info.append(file_info)
    # Try to read the files
    # opened_raw_file = read_raw_files(files_info)
    # Save files as ...
    converted_file_paths = convert_raw_files(raw_files_info)
    opened_converted_files = read_processed_files(converted_file_paths)
    converted_files_info = []
    for converted_file in converted_file_paths:
        file_info = file_integrity_checking(converted_file)
        if file_info["file_integrity"]:
            converted_files_info.append(file_info)

    contigous_files_list = split_files(converted_files_info)
