import os
from typing import Dict, Any

import xarray as xr
from xarray import Dataset

from oceanstream.report import start_profiling, end_profiling
from .shoal_process import write_shoals_to_csv, process_shoals
from .shoal_detection_handler import attach_shoal_mask_to_ds


def get_shoals_list(ds: xr.Dataset, profiling_info: Dict, config) -> tuple[Any, dict, Dataset]:
    parameters = config["shoals"]["parameters"]
    method = config["shoals"]["method"]

    start_time = None
    start_cpu = None
    start_memory = None

    if config["profile"]:
        start_time, start_cpu, start_memory = start_profiling()

    # Attach shoal mask to dataset
    shoal_dataset = attach_shoal_mask_to_ds(ds, parameters=parameters, method=method)

    # Process shoals
    shoal_list = process_shoals(shoal_dataset)

    if config["profile"]:
        profiling_info["shoal detection"] = end_profiling(start_time, start_cpu, start_memory)

    return shoal_list, profiling_info, shoal_dataset


def write_csv(ds: xr.Dataset, profiling_info: Dict, config):
    shoal_list = None
    shoal_dataset = None

    if config["shoals"]["enabled"]:
        shoal_list, profiling_info, shoal_dataset = get_shoals_list(ds, profiling_info=profiling_info,
                                                                    config=config)
        if config["export_csv"]:
            write_shoals_to_csv(shoal_list,
                                os.path.join(config["output_folder"], config["raw_path"].stem + "_fish_schools.csv"))

    return shoal_list, shoal_dataset
