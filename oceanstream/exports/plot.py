from pathlib import Path
from typing import Optional, Union

import matplotlib.pyplot as plt
import numpy as np
import xarray as xr


def plot_all_channels(
    dataset1: xr.Dataset,
    dataset2: Optional[xr.Dataset] = None,
    variable_name: str = "Sv",
    name: str = "",
    save_path: Optional[Union[str, Path]] = "",
    **kwargs,
):
    """
    Plots echograms for all channels from one or two xarray Datasets.

    This function iterates over channels in the specified variable of the given dataset(s) and creates echogram plots.
    Each channel's data is plotted in a separate figure. When two datasets are provided, their respective echograms
    for each channel are plotted side by side for comparison.

    Parameters:
    - dataset1 (xr.Dataset): The first xarray Dataset to plot.
    - dataset2 (xr.Dataset, optional): The second xarray Dataset to plot alongside the first. Defaults to None.
    - variable_name (str, optional): The name of the variable to plot from the dataset. Defaults to "Sv".
    - name (str, optional): Base name for the output plot files. Defaults to empty string"".
    - save_path ((str, Path) optional): Path where to save the images default is current working dir.
    - **kwargs: Arbitrary keyword arguments. Commonly used for plot customization like `vmin`, `vmax`, and `cmap`.

    Saves:
    - PNG files for each channel's echogram, named using the variable name, the `name` parameter and channel name.

    Example:
    >> plot_all_channels(dataset1, dataset2, variable_name="Sv", name="echogram", vmin=-70, vmax=-30, cmap='inferno')
    This will create and save echogram plots comparing dataset1 and dataset2 for each channel, using specified plot settings.

    Note:
    - If only one dataset is provided, echograms for that dataset alone will be plotted.
    - The function handles plotting parameters such as color range (`vmin` and `vmax`) and colormap (`cmap`) via kwargs.
    """
    for ch in dataset1[variable_name].channel.values:
        plt.figure(figsize=(20, 10))

        # Configure plotting parameters
        plot_params = {
            "vmin": kwargs.get("vmin", -100),
            "vmax": kwargs.get("vmax", -40),
            "cmap": kwargs.get("cmap", "viridis"),
        }

        if dataset2:
            # First subplot for dataset1
            ax1 = plt.subplot(1, 2, 1)
            mappable1 = ax1.pcolormesh(
                np.rot90(dataset1[variable_name].sel(channel=ch).values), **plot_params
            )
            plt.title(f"Original Data {ch}")

            # Second subplot for dataset2
            ax2 = plt.subplot(1, 2, 2)
            ax2.pcolormesh(np.rot90(dataset2[variable_name].sel(channel=ch).values), **plot_params)
            plt.title(f"Downsampled Data {ch}")

            # Create a common colorbar
            plt.colorbar(mappable1, ax=[ax1, ax2], orientation="vertical")

        else:
            ax = plt.subplot(1, 1, 1)
            plt.pcolormesh(np.rot90(dataset1[variable_name].sel(channel=ch).values), **plot_params)
            plt.title(f"{variable_name} Data {ch}")

            # Create a colorbar
            plt.colorbar(ax=ax, orientation="vertical")

        # Save the figure
        if save_path:
            used_path = Path(save_path)
            used_path = used_path / f"{name}_{variable_name}_channel_{ch}.png"
        else:
            used_path = f"{name}_{variable_name}_channel_{ch}.png"
        plt.savefig(used_path)
        plt.close()
