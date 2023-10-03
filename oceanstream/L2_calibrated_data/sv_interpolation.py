"""
sv_interpolation.py
-------------------
Description: Module dedicated to the interpolation of acoustic backscatter data in echosounder datasets.
It provides utilities for converting between decibel and linear scales, applying various masks to the data,
and performing interpolation to fill missing or NaN values. The module supports both direct `xr.Dataset`
inputs and file path inputs, ensuring flexibility in data processing workflows. Additionally,
it offers edge filling capabilities to enhance the quality of interpolated echograms.
"""
from pathlib import Path
from typing import Union

import numpy as np
import xarray as xr

from oceanstream.L2_calibrated_data.processed_data_io import read_processed


def db_to_linear(db: xr.DataArray) -> xr.DataArray:
    """Convert decibel to linear scale, handling NaN values."""
    linear = xr.where(db.isnull(), np.nan, 10 ** (db / 10))
    return linear


def linear_to_db(linear: xr.DataArray) -> xr.DataArray:
    """Convert linear to decibel scale, handling NaN values."""
    db = xr.where(linear.isnull(), np.nan, 10 * np.log10(linear))
    return db


def interpolate_sv(
    sv: Union[xr.Dataset, str, Path], method: str = "linear", with_edge_fill: bool = False
) -> xr.Dataset:
    """
    Apply masks to the Sv DataArray in the dataset and interpolate over the resulting NaN values.

    Parameters:
    - Sv (Union[xr.Dataset, str, Path]): Dataset or path to the netCDF or zarr file.
    - method (str): Interpolation method.
    - with_edge_fill (bool): Flag to allow filling the edges of echograms

    Returns:
    - xr.Dataset: Dataset with the masked and interpolated Sv DataArray.

    Example:
    >> interpolate_sv(Sv, method)
    Expected Output
    """
    # Load the dataset
    if isinstance(sv, xr.Dataset):
        dataset = sv
    else:
        path_to_file = Path(sv)
        dataset = read_processed(path_to_file)

    # Retrieve the Sv DataArray from the dataset
    sv_dataarray = dataset["Sv"]

    # Initialize an empty list to store the processed channels
    processed_channels = []

    # Loop over each channel
    for channel in sv_dataarray["channel"]:
        channel_data = sv_dataarray.sel(channel=channel)

        # Convert from dB to linear scale
        channel_data_linear = db_to_linear(channel_data)

        # Apply the masks
        for var_name in dataset.data_vars:
            if var_name.startswith("mask_"):
                mask = dataset[var_name].sel(channel=channel)
                channel_data_linear = channel_data_linear.where(mask, np.nan)

        # Perform interpolation to fill NaN values in linear scale
        # Assuming you are interpolating over ping_time and range dimensions

        interpolated_channel_data_linear = channel_data_linear.interpolate_na(
            dim="ping_time", method=method
        )

        if with_edge_fill:
            # interpolated_channel_data_linear = interpolated_channel_data_linear.interpolate_na(dim='range_sample',
            #                                                                                   method=method)
            interpolated_channel_data_linear = interpolated_channel_data_linear.ffill(
                dim="ping_time"
            )
            interpolated_channel_data_linear = interpolated_channel_data_linear.bfill(
                dim="ping_time"
            )

        # Convert back to dB scale
        interpolated_channel_data = linear_to_db(interpolated_channel_data_linear)

        # Append the processed channel data to the list
        processed_channels.append(interpolated_channel_data)

    # Combine the processed channels back into a single DataArray
    interpolated_sv = xr.concat(processed_channels, dim="channel")

    # Update the Sv DataArray in the dataset with the interpolated values
    dataset["Sv"] = interpolated_sv

    return dataset
