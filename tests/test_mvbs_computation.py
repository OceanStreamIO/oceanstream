import numpy as np
import pandas as pd
import pytest
import xarray as xr
from echopype.commongrid.api import compute_MVBS, compute_MVBS_index_binning

from oceanstream.L3_regridded_data.mvbs_computation import compute_mvbs


def generate_mock_data(channels=2, pings=4, ranges=4):
    """
    Generate a mock dataset with given dimensions.

    Parameters:
    - channels (int): Number of channels.
    - pings (int): Number of ping times.
    - ranges (int): Number of range samples.

    Returns:
    - Mock dataset (xarray.DataArray).
    """
    # Data
    data = np.array(
        [
            [[-80, 0, 0, 0], [-80, 0, 0, 0], [-80, 0, 0, 0], [-80, 0, 0, 0]],  # Channel 1
            [[-1, 0, 0, 0], [-1, 0, 0, 0], [-1, 0, 0, 0], [-1, 0, 0, 0]],  # Channel 2
        ]
    )

    # Channel names
    channel_names = ["Channel " + str(i + 1) for i in range(channels)]

    # Create datetime range for ping times
    ping_times = pd.date_range("2017-06-20T01:10:27", periods=pings, freq="S")

    # Range sample values
    range_sample = np.arange(ranges)

    # Create the xarray DataArray
    sv = xr.DataArray(
        data=data,
        coords={"channel": channel_names, "ping_time": ping_times, "range_sample": range_sample},
        dims=["channel", "ping_time", "range_sample"],
    )

    return sv


def test_index_binning_wrong_params():
    ds = generate_mock_data(2, 4, 4)
    with pytest.raises(
        ValueError,
        match="For 'index_binning' method, only range_sample_num and ping_num should be provided.",
    ):
        compute_mvbs(ds, method="index_binning", range_var="depth")
    with pytest.raises(
        ValueError,
        match="For 'index_binning' method, only range_sample_num and ping_num should be provided.",
    ):
        compute_mvbs(ds, method="index_binning", range_bin="30m")
    with pytest.raises(
        ValueError,
        match="For 'index_binning' method, only range_sample_num and ping_num should be provided.",
    ):
        compute_mvbs(ds, method="index_binning", ping_time_bin="30S")


def test_physical_units_wrong_params():
    ds = generate_mock_data(2, 4, 4)
    with pytest.raises(
        ValueError,
        match="For 'physical_units' method, only range_var, range_bin, and ping_time_bin should be provided.",
    ):
        compute_mvbs(ds, method="physical_units", range_sample_num=150)
    with pytest.raises(
        ValueError,
        match="For 'physical_units' method, only range_var, range_bin, and ping_time_bin should be provided.",
    ):
        compute_mvbs(ds, method="physical_units", ping_num=150)


def test_compute_mvbs(enriched_ek60_Sv):
    enriched_sv = enriched_ek60_Sv
    ds_ep = compute_MVBS_index_binning(enriched_sv)
    ds_os = compute_mvbs(enriched_sv, method="index_binning")
    result = np.isclose(ds_ep["Sv"].values, ds_os["Sv"].values, atol=1e-8, equal_nan=True)
    assert result.all()
    ds_ep = compute_MVBS(enriched_sv)
    ds_os = compute_mvbs(enriched_sv, method="physical_units")
    result = np.isclose(ds_ep["Sv"].values, ds_os["Sv"].values, atol=1e-8, equal_nan=True)
    assert result.all()
    ds_ep = compute_MVBS_index_binning(enriched_sv, range_sample_num=30, ping_num=30)
    ds_os = compute_mvbs(enriched_sv, method="index_binning", range_sample_num=30, ping_num=30)
    result = np.isclose(ds_ep["Sv"].values, ds_os["Sv"].values, atol=1e-8, equal_nan=True)
    assert result.all()
    ds_ep = compute_MVBS(enriched_sv, range_var="depth", range_bin="90m", ping_time_bin="60S")
    ds_os = compute_mvbs(
        enriched_sv,
        method="physical_units",
        range_var="depth",
        range_bin="90m",
        ping_time_bin="60S",
    )
    result = np.isclose(ds_ep["Sv"].values, ds_os["Sv"].values, atol=1e-8, equal_nan=True)
    assert result.all()
