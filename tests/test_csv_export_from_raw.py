from oceanstream.L3_regridded_data.csv_export_from_raw import *


def test_create_metadata(raw_dataset_jr179):
    data = create_metadata(raw_dataset_jr179)
    assert data.shape == (36, 3)


def test_create_calibration(raw_dataset_jr179):
    data = create_calibration(raw_dataset_jr179)
    assert data.shape == (15, 4)
