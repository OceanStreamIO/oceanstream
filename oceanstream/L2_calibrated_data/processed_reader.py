"""
processed_reader.py
-------------------------
Description: Brief description of what this module does.

"""

from pathlib import Path

# Import necessary libraries
from typing import Union

import xarray as xr


def read_processed(file_path: Union[str, Path]) -> xr.Dataset:
    """
    Read and return a xarray Dataset from a specified file path.

    Parameters:
    - file_path (Union[str, Path]): The path to the file to be read.

    Returns:
    - xr.Dataset: The xarray Dataset read from the file.

    Raises:
    - ValueError: If the file does not exist or has an unsupported format.

    Example:
    >> ds = read_processed("/path/to/datafile.nc")
    """

    # Convert the input to a Path object (if it isn't already)
    file_path = Path(file_path)

    # Check if the file exists
    if not file_path.exists():
        raise ValueError(f"File does not exist: {file_path}")

    # Check if the file has a supported format
    if file_path.suffix not in [".nc", ".zarr"]:
        raise ValueError(f"Unsupported file format: {file_path.suffix}")

    # Read the file based on its format
    # Read the file based on its format and load data into memory
    if file_path.suffix == ".nc":
        with xr.open_dataset(file_path) as ds:
            dataset = ds.load()

    elif file_path.suffix == ".zarr":
        with xr.open_zarr(file_path) as ds:
            dataset = ds.load()
    else:
        raise Exception("Could not open file")

    return dataset


def write_processed(
    sv: xr.Dataset,
    file_path: Union[str, Path],
    file_name: str = "",
    file_type: str = "nc",
    overwrite: bool = True,
):
    """
    Save a xarray Dataset to a specified path with a given file name and type.

    Parameters:
    - sv (xr.Dataset): The xarray Dataset to save.
    - file_path (Union[str, Path]): The directory path where the file should be saved.
    - file_name (str, optional): The name of the file. Defaults to the name of the Dataset.
    - file_type (str, optional): The type of the file, either 'nc' or 'zarr'. Defaults to 'nc'.
    - overwrite (bool, optional): Whether to overwrite the file if it already exists. Defaults to True.

    Returns:
    - None

    Raises:
    - TypeError: If the provided Dataset is not an instance of xr.Dataset.
    - ValueError: For invalid paths, unsupported file formats, or other invalid inputs.

    Example:
    >> write_processed(dataset, "/path/to/save", "datafile", "nc")
    """
    if not isinstance(sv, xr.Dataset):
        raise TypeError("Expected a xarray Dataset")

    path = Path(file_path)
    if not path.is_dir():
        raise ValueError(f"Invalid path provided: {path}")

    if not file_name:
        file_name = Path(sv.source_filenames[0].values.item()).stem

    if "." not in file_name:
        if file_type not in ["nc", "zarr"]:
            raise ValueError("File type has to be one of ['nc','zarr']")
        file_name = f"{file_name}.{file_type}"
    elif file_name.split(".")[1] not in ["nc", "zarr"]:
        raise ValueError(f"File name provided has unsupported format: {file_name}")

    full_path = path / file_name

    if full_path.is_file() and not overwrite:
        return

    if full_path.suffix == ".nc":
        sv.to_netcdf(full_path)
    elif full_path.suffix == ".zarr":
        sv.to_zarr(full_path, mode="w")
    else:
        raise ValueError(f"Could not save file to provided path: {full_path}")


if __name__ == "__main__":
    # Code to be executed if this module is run as a standalone script
    # For example, for testing purposes
    pass
