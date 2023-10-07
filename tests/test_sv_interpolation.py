import numpy as np
import pytest
from pathlib import Path
import xarray as xr

from oceanstream.L2_calibrated_data.sv_computation import compute_sv
from oceanstream.L2_calibrated_data.sv_interpolation import (db_to_linear,
                                                             interpolate_sv,
                                                             linear_to_db)
from oceanstream.L2_calibrated_data.noise_masks import (create_impulse_mask,
                                                        create_transient_mask,
                                                        create_attenuation_mask,
                                                        attach_mask_to_dataset,
                                                        add_metadata_to_mask)
from oceanstream.L2_calibrated_data.processed_data_io import write_processed, read_processed
from tests.conftest import TEST_DATA_FOLDER

from echopype.clean.impulse_noise import (
    RYAN_DEFAULT_PARAMS,
    RYAN_ITERABLE_DEFAULT_PARAMS,
    WANG_DEFAULT_PARAMS,
)

# Sample data for testing
sample_db_data = xr.DataArray([10, 20, 30], dims="x")
sample_linear_data = xr.DataArray([1, 100, 1000], dims="x")
sample_dataset = xr.Dataset({
    'Sv': (['ping_time', 'channel'], np.array([[10, 20], [30, 40]])),
    'channel': [1, 2],
    'ping_time': [1, 2]
})
# Sample mask data for testing
sample_mask = xr.DataArray([[True, False], [False, True]], dims=["ping_time", "channel"])

# Sample dataset with masks
sample_dataset_with_mask = sample_dataset.copy()
sample_dataset_with_mask['mask_transient'] = sample_mask


def test_db_to_linear():
    expected_output = xr.DataArray([10 ** (10 / 10), 10 ** (20 / 10), 10 ** (30 / 10)], dims="x")
    assert db_to_linear(sample_db_data).equals(expected_output)


def test_linear_to_db():
    expected_output = xr.DataArray([10 * np.log10(1), 10 * np.log10(100), 10 * np.log10(1000)], dims="x")
    assert linear_to_db(sample_linear_data).equals(expected_output)


def test_interpolate_sv_with_dataset_input(complete_dataset_jr179):
    metadata = {"mask_type": "impulse"}
    source_sv = complete_dataset_jr179
    mask = create_impulse_mask(source_sv, parameters=RYAN_DEFAULT_PARAMS)
    mask_with_metadata = add_metadata_to_mask(mask, metadata)
    dataset_with_mask = attach_mask_to_dataset(source_sv, mask_with_metadata)
    interpolated_dataset = interpolate_sv(dataset_with_mask)
    assert isinstance(interpolated_dataset, xr.Dataset)
    assert 'Sv' in interpolated_dataset.data_vars


def test_interpolate_sv_with_nc_path_input(complete_dataset_jr179):
    # Assuming a sample netCDF file named "sample.nc" exists in the current directory
    metadata = {"mask_type": "impulse"}
    source_sv = complete_dataset_jr179
    mask = create_impulse_mask(source_sv, parameters=RYAN_DEFAULT_PARAMS)
    mask_with_metadata = add_metadata_to_mask(mask, metadata)
    dataset_with_mask = attach_mask_to_dataset(source_sv, mask_with_metadata)
    write_processed(dataset_with_mask, file_path=TEST_DATA_FOLDER, file_name="sample.nc")
    saved_file_path = Path(TEST_DATA_FOLDER, "sample.nc")
    interpolated_dataset = interpolate_sv(saved_file_path)
    assert isinstance(interpolated_dataset, xr.Dataset)
    assert 'Sv' in interpolated_dataset.data_vars


def test_interpolate_sv_with_zarr_path_input(complete_dataset_jr179):
    # Assuming a sample zarr directory named "sample.zarr" exists in the current directory
    # Assuming a sample netCDF file named "sample.nc" exists in the current directory
    metadata = {"mask_type": "impulse"}
    source_sv = complete_dataset_jr179
    mask = create_impulse_mask(source_sv, parameters=RYAN_DEFAULT_PARAMS)
    mask_with_metadata = add_metadata_to_mask(mask, metadata)
    dataset_with_mask = attach_mask_to_dataset(source_sv, mask_with_metadata)
    write_processed(dataset_with_mask, file_path=TEST_DATA_FOLDER, file_name="sample.zarr")
    saved_file_path = Path(TEST_DATA_FOLDER, "sample.zarr")
    interpolated_dataset = interpolate_sv(saved_file_path)
    assert isinstance(interpolated_dataset, xr.Dataset)
    assert 'Sv' in interpolated_dataset.data_vars


def test_interpolate_sv_output_type():
    interpolated_dataset = interpolate_sv(sample_dataset)
    assert isinstance(interpolated_dataset, xr.Dataset)


def test_interpolation_fills_nan():
    interpolated_dataset = interpolate_sv(sample_dataset_with_mask)
    assert not interpolated_dataset['Sv'].isel(ping_time=0, channel=0).isnull()


def test_edge_filling_functionality():
    interpolated_dataset = interpolate_sv(sample_dataset_with_mask, with_edge_fill=True)
    assert not interpolated_dataset['Sv'].isel(ping_time=0, channel=0).isnull()


def test_interpolation_methods():
    for method in ["linear", "nearest"]:
        interpolated_dataset = interpolate_sv(sample_dataset_with_mask, method=method)
        assert isinstance(interpolated_dataset, xr.Dataset)
        assert 'Sv' in interpolated_dataset.data_vars


def test_invalid_inputs():
    # Non-xarray input
    with pytest.raises(FileNotFoundError):
        interpolate_sv("invalid_input")

    # Invalid file paths
    with pytest.raises(FileNotFoundError):
        interpolate_sv(Path("non_existent_file.nc"))


def test_empty_or_all_nan_datasets():
    empty_dataset = xr.Dataset()
    all_nan_dataset = xr.Dataset({'Sv': (('ping_time', 'channel'), np.full((5, 5), np.nan))})

    # Empty dataset
    with pytest.raises(KeyError):
        interpolate_sv(empty_dataset)

    # All NaN dataset
    result = interpolate_sv(all_nan_dataset)
    assert result['Sv'].isnull().all()


def test_missing_sv_or_channel():
    missing_sv_dataset = xr.Dataset({'Not_Sv': (('ping_time', 'channel'), np.random.rand(5, 5))})
    missing_channel_dataset = xr.Dataset({'Sv': (('ping_time',), np.random.rand(5))})

    # Missing 'Sv' DataArray
    with pytest.raises(KeyError):
        interpolate_sv(missing_sv_dataset)

    # Missing 'channel' dimension
    with pytest.raises(KeyError):
        interpolate_sv(missing_channel_dataset)


def test_retains_metadata_and_other_dataarrays(complete_dataset_jr179):
    metadata = {"mask_type": "impulse"}
    source_sv = complete_dataset_jr179
    mask = create_impulse_mask(source_sv, parameters=RYAN_DEFAULT_PARAMS)
    mask_with_metadata = add_metadata_to_mask(mask, metadata)
    dataset_with_mask = attach_mask_to_dataset(source_sv, mask_with_metadata)

    result = interpolate_sv(dataset_with_mask)

    # Check metadata
    assert dataset_with_mask.attrs == result.attrs

    # Check coordinates
    for coord in dataset_with_mask.coords:
        assert np.array_equal(dataset_with_mask[coord], result[coord])

    # Check other DataArrays
    for data_var in dataset_with_mask.data_vars:
        if data_var != 'Sv':
            assert np.array_equal(dataset_with_mask[data_var], result[data_var])


def test_deterministic_behavior(complete_dataset_jr179):
    metadata = {"mask_type": "impulse"}
    source_sv = complete_dataset_jr179
    mask = create_impulse_mask(source_sv, parameters=RYAN_DEFAULT_PARAMS)
    mask_with_metadata = add_metadata_to_mask(mask, metadata)
    dataset_with_mask1 = attach_mask_to_dataset(source_sv, mask_with_metadata)
    dataset_with_mask2 = dataset_with_mask1.copy(deep=True)
    print(np.isnan(dataset_with_mask1['Sv']).sum())
    print(np.isnan(dataset_with_mask2['Sv']).sum())
    assert np.allclose(dataset_with_mask1['Sv'].values, dataset_with_mask2['Sv'].values, equal_nan=True, atol=1e-8)

    result1 = interpolate_sv(dataset_with_mask1)
    result2 = interpolate_sv(dataset_with_mask2)

    assert np.array_equal(result1['Sv'], result2['Sv'],equal_nan=True)
