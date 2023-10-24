# import echopype as ep
# import pandas as pd
import xarray as xr


def create_metadata(data: xr.Dataset):
    """
    Given a raw echodata file, it extracts the metadata we require
    :param data: xr.Dataset: the raw data to extract this information from
    :return: pd.Dataframe: the required metadata
    """
    bg_1 = data["Sonar/Beam_group1"].isel(ping_time=0).isel(range_sample=0)
    bg_1.set_coords("frequency_nominal")
    variable_list = [
        "frequency_nominal",
        "beamwidth_twoway_alongship",
        "beamwidth_twoway_athwartship",
        "angle_offset_alongship",
        "angle_offset_athwartship",
        "angle_sensitivity_alongship",
        "angle_sensitivity_athwartship",
        "equivalent_beam_angle",
        "gpt_software_version",
        "transmit_bandwidth",
        "transmit_duration_nominal",
        "transmit_power",
    ]
    df = (
        bg_1.drop_vars([v for v in bg_1.variables if v not in variable_list])
        .to_dataframe()
        .transpose()
    )
    df.columns = df.loc["frequency_nominal"]
    df = df.loc[[r for r in df.index if r != "frequency_nominal"]]
    df["vars"] = df.index
    df = df.melt(id_vars="vars")
    df.columns = ["Name", "Frequency", "Value"]
    return df


def create_calibration(data: xr.Dataset):
    """
    Given a raw echodata file, it extracts the calibration data we require
    :param data: xr.Dataset: the raw data to extract this information from
    :return: pd.Dataframe: the required calibration data
    """
    df = data["Vendor_specific"].to_dataframe()
    columns = ["frequency_nominal", "pulse_length", "gain_correction", "sa_correction"]
    df = df[columns]
    df.columns = ["Frequency", "Pulse_length", "Gain", "Sa"]
    return df


def export_raw_csv(data: xr.Dataset, folder: str, root_name: str):
    """
    Given a raw echodata file, a folder to write the outputs into and a name pattern for the files,
    it extracts and exports to csv the calibration data and the metadata

    :param data: xr.Dataset: the raw data to extract this information from
    :param folder: str: the folder name to use
    :param root_name: the root name to be used in the file patterns
    :return:
    """
    metadata = create_metadata(data)
    calibration = create_calibration(data)
    metadata_filename = folder + "/" + root_name + "_metadata.csv"
    calibration_filename = folder + "/" + root_name + "_calibration.csv"
    try:
        metadata.to_csv(metadata_filename, index=False)
        calibration.to_csv(calibration_filename, index=False)
    except Exception as e:
        raise ValueError(str(e))
