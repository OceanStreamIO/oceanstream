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

import echopype as ep


def file_finder(paths):
    """
    This functions find all the raw files
    that could be appended into a Dataset.

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
            if ".raw" in elem and os.path.isfile(elem):
                files.append(elem)
    else:
        raise ValueError(
            "Invalid input. Provide either a directory\
             path or a list of file paths."
        )

    return sorted(files)


def file_checking(file):
    """
    This functions checks the time range of one file and
    if it could be appended into a Dataset.

    Parameters:
    - file (str): file should be an absolute path
    to a raw file.

    Returns:
    - date range: the date range the file covers
    - file_integrity: if the raw file is readeble

    Example:
    file_checking(paths)
    Expected Output
    """
    ed = ep.open_raw(file, sonar_model="EK60")
    if ed:
        date_range = [1, 0]
        file_integrity = True
    else:
        date_range = [0, 1]
        file_integrity = False
    return date_range, file_integrity


# Additional functions...


if __name__ == "__main__":
    # Code to be executed if this module is run as a standalone script
    # For example, for testing purposes

    # Get list of files
    path = r"C:\Users\mishu\OneDrive\Desktop\pinelab\test_data\ek60"
    files = file_finder(path)
    print(files)

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
    files = file_finder(files)
    print(files)
    # Check to be raw files
    for file in files:
        print(file_checking(file))
    # Check to make sure they are ordered and from similar date range

    # Try to read the files and concatenate them

    # Save files as ...
