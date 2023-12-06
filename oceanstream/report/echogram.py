import os
import xarray as xr
import matplotlib
import matplotlib.pyplot as plt
import echopype as ep


# def save_echogram_to_file(ds: xr.Dataset, config: dict, filename):
#     """
#     Generates an echogram from an xarray dataset and saves it to a file.
#
#     Parameters:
#     - ds (xr.Dataset): The echosounder xarray dataset.
#     - config (dict): Configuration dictionary containing output folder and other settings.
#     """
#     # Generate echogram
#     echograms = ep.visualize.create_echogram(ds, get_range=True, robust=True, vmin=-80, vmax=-50)
#
#     for idx, echogram in enumerate(echograms):
#         filename = f"{filename}_{idx}.png"
#         output_folder = config.get('output_folder', '.')
#         output_path = os.path.join(output_folder, filename)
#         echogram.fig.savefig(output_path)
#
#         # Create a figure and axis to plot the echogram
#         fig, ax = plt.subplots(figsize=(10, 6))
#         cax = ax.imshow(echogram_data, aspect='auto')
#
#         fig.colorbar(cax, ax=ax)
#
#         # Set plot properties (optional)
#         ax.set_title("Echogram " + filename)
#         ax.set_xlabel("X-axis Label")
#         ax.set_ylabel("Depth (m)")
#
#
#         # Create output folder if it doesn't exist
#         if not os.path.exists(output_folder):
#             os.makedirs(output_folder)
#
#         # Save the figure
#         plt.savefig(output_path, dpi=300)
#         plt.close(fig)
#
#     plt.close('all')

def save_echogram_to_file_combined(ds: xr.Dataset, config: dict, filename: str):
    """
    Generates echograms from an xarray dataset and saves them to a single file.

    Parameters:
    - ds (xr.Dataset): The echosounder xarray dataset.
    - config (dict): Configuration dictionary containing additional echogram settings.
    - filename (str): The filename for the saved echogram.
    """
    # Generate echograms
    echograms = ep.visualize.create_echogram(ds, get_range=True, robust=True, vmin=-80, vmax=-50)

    # Combine echograms vertically in a new figure
    num_echograms = len(echograms)
    total_height = sum(eg.fig.get_size_inches()[1] for eg in echograms)
    combined_fig, axs = plt.subplots(num_echograms, 1, figsize=(8, total_height))

    # Ensure axs is iterable
    if num_echograms == 1:
        axs = [axs]

    for ax, echogram in zip(axs, echograms):
        for orig_ax in echogram.axes.flatten():
            # Here we assume the echogram uses pcolormesh. Adjust as needed for other plot types.
            for quadmesh in orig_ax.get_children():
                if isinstance(quadmesh, matplotlib.collections.QuadMesh):
                    data = quadmesh.get_array()
                    mesh = ax.pcolormesh(data, cmap=quadmesh.get_cmap(), norm=quadmesh.norm)
                    mesh.set_clip_box(quadmesh.get_clip_box())
                    mesh.set_clim(quadmesh.get_clim())
                    mesh.sticky_edges.x[:] = quadmesh.sticky_edges.x[:]
                    mesh.sticky_edges.y[:] = quadmesh.sticky_edges.y[:]

                    # Copy colorbar properties
                    orig_cbar = orig_ax.collections[0].colorbar
                    if orig_cbar:
                        new_cbar = plt.colorbar(mesh, ax=ax, orientation=orig_cbar.orientation)
                        new_cbar.set_label(orig_cbar.ax.get_ylabel())

    # Adjust layout and save the figure
    plt.tight_layout()
    output_path = os.path.join(config.get('output_folder', '.'), filename)
    combined_fig.savefig(output_path, dpi=300)
    plt.close(combined_fig)