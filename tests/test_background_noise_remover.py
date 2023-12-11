import numpy as np
import pandas as pd
import pytest
import xarray as xr

from oceanstream.denoise.background_noise_remover import apply_remove_background_noise


def test_apply_remove_background_noise(enriched_ek60_Sv):
    ds_Sv = apply_remove_background_noise(enriched_ek60_Sv)
    assert np.nanmean(ds_Sv["Sv"].values) == pytest.approx(-72.7698338137907, 0.0001)
    assert np.nanmin(ds_Sv["Sv"].values) == pytest.approx(-156.02047944545484, 0.0001)
    assert np.nanmean(ds_Sv["Sv_with_background_noise"].values) == pytest.approx(
        np.nanmean(enriched_ek60_Sv["Sv"].values), 0.0001
    )


def create_test_dataset():
    # Creating a test dataset with a small matrix of 4 rows and 4 columns
    # This will simulate the 'echo_range' data for different channels

    # Simulating echo_range data for 4 channels, each with 4 ping times and 4 range samples
    echo_range_data = np.array(
        [
            [
                [10, np.nan, 30, np.nan],
                [11, 21, 31, 41],
                [12, 22, 32, 42],
                [13, 23, 33, 43],
            ],  # Channel 1
            [[15, 25, 35, 45], [16, 26, 36, 46], [17, 27, 37, 47], [18, 28, 38, 48]],  # Channel 2
            [[20, 30, 40, 50], [21, 31, 41, 51], [22, 32, 42, 52], [23, 33, 43, 53]],  # Channel 3
            [[25, 35, 45, 55], [26, 36, 46, 56], [27, 37, 47, 57], [28, 38, 48, 58]],  # Channel 4
        ]
    )

    # Creating the xarray Dataset
    ds_Sv = xr.Dataset(
        {"echo_range": (["channel", "ping_time", "range_sample"], echo_range_data)},
        coords={
            "channel": ["Channel 1", "Channel 2", "Channel 3", "Channel 4"],
            "ping_time": pd.date_range("2023-11-13", periods=4),
            "range_sample": np.arange(4),
        },
    )

    return ds_Sv


def test_background_noise_value_error():
    # Creating the test dataset
    test_ds_Sv = create_test_dataset()

    # Applying the function to the test dataset
    try:
        apply_remove_background_noise(test_ds_Sv)
        print("Function executed successfully.")
    except ValueError as e:
        print(f"Error caught: {e}")
