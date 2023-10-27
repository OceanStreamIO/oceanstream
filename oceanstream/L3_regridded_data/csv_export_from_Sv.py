import pandas as pd
import xarray as xr
from haversine import haversine


def create_location(data: xr.Dataset) -> pd.DataFrame:
    """
    Given a processed Sv file, enriched with lat/lon, it returns location data:
        lat,lon,time, speed

    Parameters:
    - data: xr.Dataset
        The raw data to extract information from.

    Returns:
    - pd.DataFrame
        The required metadata.
    """
    df = data.drop_vars(
        [v for v in data.variables if v not in ["latitude", "longitude"]]
    ).to_dataframe()
    df["dt"] = data.coords["ping_time"]
    df.columns = ["lat", "lon", "dt"]
    df["distance"] = [
        haversine(
            (df["lat"].iloc[i], df["lon"].iloc[i]),
            (df["lat"].iloc[i - 1], df["lon"].iloc[i - 1]),
            unit="nmi",
        )
        if i > 0
        else 0
        for i in range(len(df))
    ]
    df["time_interval"] = df["dt"] - df["dt"].shift()
    df["knt"] = (df["distance"] / df["time_interval"].dt.total_seconds()) * 3600
    df = df[["lat", "lon", "dt", "knt"]]

    return df


def create_Sv(data: xr.Dataset, channel: str) -> pd.DataFrame:
    """
    Given a processed Sv file, enriched with lat/lon, it returns Sv data

    Parameters:
    - data: xr.Dataset
        The raw data to extract information from.
    - channel: str
        The channel to use

    Returns:
    - pd.DataFrame
        The required data.
    """
    df = data.sel(channel=channel)["Sv"].to_dataframe()
    df = df["Sv"].unstack(level="range_sample")
    return df


def export_Sv_csv(data: xr.Dataset, folder: str, root_name: str):
    """
    Given a Sv file, a folder to write the outputs into, and a name pattern for the files,
    it extracts and exports to CSV the location data and the Sv data

    Parameters:
    - data: xr.Dataset
        The Sv to extract this information from.
    - folder: str
        The folder name to use.
    - root_name: str
        The root name to be used in the file patterns.

    Returns:
    - None
    """
    location = create_location(data)
    Sv = create_Sv(data, data["channel"][0])  # for R Shiny compat reasons
    location_filename = folder + "/" + root_name + "_GPS.csv"
    Sv_filename = folder + "/" + root_name + "_Sv.csv"
    try:
        location.to_csv(location_filename, index=False)
        Sv.to_csv(Sv_filename, index=False)
    except Exception as e:
        raise ValueError(str(e))
