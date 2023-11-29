from pathlib import Path
from typing import Dict, List, Optional, Union

import matplotlib.pyplot as plt
import numpy as np
import xarray as xr


def dict_to_formatted_list(d: Dict[str, Union[int, str]]) -> List[str]:
    """Convert a dictionary to a list of formatted strings."""
    return [f"{key}={value}" for key, value in d.items()]


def add_metadata_to_mask(mask: xr.Dataset, metadata: Dict) -> xr.Dataset:
    """
    Attaches the provided metadata to the given mask as global attributes.

    Parameters:
    - mask (xarray.Dataset): mask to be attached
    - metadata (dict): dictionary of metadata

    Returns:
    - xarray.Dataset: mask with metadata stored as global attributes

    Example:
        >>> add_metadata_to_mask(mask, metadata={"mask_type": "transient",
                                    "interpolation": "median_filtering"})
    Expected Output:
    A mask with the metadata stored as global attributes
    """
    for k, v in metadata.items():
        mask.attrs[k] = v
    return mask


def attach_mask_to_dataset(Sv: xr.Dataset, mask: xr.Dataset) -> xr.Dataset:
    """
    Attaches a mask to an existing Sv dataset, allowing the mask to travel in one data structure to the next module

    Parameters:
    - Sv (xarray.Dataset): dataset to attach a mask to
    - mask (xarray.Dataset): mask to be attached, with a mask_type attribute explaining what sort of mask it is

    Returns:
    - xarray.Dataset: dataset enriched with the mask

    Example:
        >>> attach_mask_to_dataset(Sv, mask)
    Expected Output:
        Sv with an extra variable containing the mask, named mask_[mask_type]
    """
    mask_type = mask.attrs["mask_type"]
    mask_name = "mask_" + mask_type
    Sv_mask = Sv.assign(mask=mask)
    Sv_mask["mask"].attrs = mask.attrs
    Sv_mask = Sv_mask.rename({"mask": mask_name})
    return Sv_mask


def attach_masks_to_dataset(Sv: xr.Dataset, masks: [xr.Dataset]) -> xr.Dataset:
    """
    Attaches masks to an existing Sv dataset,
    so they can travel in one data structure to the next module

    Parameters:
    - Sv (xarray.Dataset): dataset to attach the masks to
    - masks (xarray.Dataset[]): masks to be attached

    Returns:
    - xarray.Dataset: dataset enriched with the masks as separate variables

    Example:
        >>> attach_masks_to_dataset(Sv, masks)
    Expected Output:
    - Sv with extra variables containing the masks, named mask_[mask_type]
    """
    for mask in masks:
        Sv = attach_mask_to_dataset(Sv, mask)
    return Sv


def tfc(mask: xr.DataArray):
    """
    Counts true and false values in a xarray (usually a mask)

    Parameters:
    - mask (xarray.DataArray): boolean xarray

    Returns:
    - (): tuple where the first value is the count of true values
    and the second one is the count of false values

    Example:
        >>> tfc(mask)
    """
    count_true = np.count_nonzero(mask)
    count_false = mask.size - count_true
    true_false_counts = (count_true, count_false)
    return true_false_counts


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
