import argparse
import asyncio
import logging
import os
import sys
import warnings
from pathlib import Path

from oceanstream.denoise import (
    apply_background_noise_removal,
    apply_noise_masks,
    apply_seabed_mask,
    create_masks,
)
from oceanstream.echodata import (
    compute_sv_with_encode_mode,
    enrich_sv_dataset,
    read_file,
    write_processed,
)
from oceanstream.exports import compute_and_write_nasc
from oceanstream.exports import write_csv as write_shoals_csv
from oceanstream.exports.csv import export_raw_csv, export_Sv_csv
from oceanstream.exports.plot import plot_all_channels
from oceanstream.report import display_profiling_and_summary_info
from oceanstream.settings import load_config
from oceanstream.utils import attach_mask_to_dataset

DEFAULT_OUTPUT_FOLDER = "output"


def parse_cli_arguments():
    parser = argparse.ArgumentParser(description="Process hydroacoustic data.")
    parser.add_argument(
        "--raw-data-source",
        type=str,
        required=True,
        help="Path to a raw data file or directory containing multiple raw data files",
    )
    parser.add_argument(
        "--output-folder",
        type=str,
        default=None,
        help="Destination path for saving processed data. Defaults to a predefined directory if not specified.",
    )
    parser.add_argument(
        "--sonar-model", type=str, help="Sonar model used to collect the data (EK60, EK80, etc.)"
    )
    parser.add_argument(
        "--export-csv", action="store_true", help="Write CSV output files with processed data"
    )
    parser.add_argument("--config", type=str, default=None, help="Path to a configuration file")
    parser.add_argument(
        "--profile", action="store_true", help="Display profiling information for mask creation"
    )
    parser.add_argument(
        "-l",
        "--log-level",
        help="Set the logging level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="WARNING",
    )

    return parser.parse_args()


async def process_file(filename, args):
    # Output the filename to the terminal
    print(f"Processing file: {filename}")

    config = load_config(args.config)
    profiling_info = {}

    initialize(args, config, filename)

    # Process the raw data. Convert to EchoData object
    echodata, encode_mode = read_file(profiling_info=profiling_info, config=config)

    # Compute Sv with encode_mode and save to zarr
    sv_dataset = compute_sv_with_encode_mode(
        echodata, encode_mode=encode_mode, profiling_info=profiling_info, config=config
    )
    write_processed(sv_dataset, config["output_folder"], config["raw_path"].stem, "zarr")
    zarr_file = config["output_folder"] + "/" + config["raw_path"].stem + ".zarr"
    print(f"Computed Sv with encode_mode={encode_mode} and wrote zarr file to: {zarr_file}")

    # Enrich the Sv by adding depth, location, and split-beam angle information
    sv_enriched = create_enriched_sv(echodata, encode_mode, sv_dataset)

    # Create noise masks
    print("Creating noise masks...")
    masks, profiling_info = create_masks(sv_enriched, profiling_info=profiling_info, config=config)

    mask_keys = []
    sv_with_masks = sv_enriched.copy(deep=True)
    if masks:
        for mask in masks:
            mask_type = mask[0]
            mask_keys.append(mask_type)
            mask_data = mask[1]
            sv_with_masks = attach_mask_to_dataset(
                sv_with_masks, mask=mask_data, mask_type=mask_type
            )

    ds_processed = apply_noise_masks(sv_with_masks, config)

    print(f"Created and applied noise masks: {mask_keys}")

    # Background noise removal
    print("Removing background noise...")
    ds_clean, profiling_info = apply_background_noise_removal(
        ds_processed, profiling_info=profiling_info, config=config
    )

    raw_csv_path = os.path.join(config["output_folder"], config["raw_path"].stem)

    # Calibration and metadata
    if config["export_csv"]:
        export_raw_csv(echodata, config["output_folder"], config["raw_path"].stem)
        export_Sv_csv(ds_clean, config["output_folder"], config["raw_path"].stem)
        print(f"Exported raw and processed CSV files to: {raw_csv_path}")

    # Seabed mask
    ds_clean = apply_seabed_mask(ds_clean, config=config)
    print("Applied seabed mask")

    # Echogram
    plot_all_channels(ds_clean, save_path=config["output_folder"])
    print(f"Saved echograms for all channels to: {config['output_folder']}")
    # save_echogram_to_file(ds_clean, config, config["raw_path"].stem + "_echogram_clean.png")

    # Shoals
    shoal_list, shoal_dataset = write_shoals_csv(
        ds_clean, profiling_info=profiling_info, config=config
    )
    print(f"Exported shoal CSV data to: {raw_csv_path}")

    # NASC
    compute_and_write_nasc(shoal_dataset, profiling_info=profiling_info, config=config)
    print(f"Exported NASC CSV data to: {raw_csv_path}")

    display_profiling_and_summary_info(profiling_info=profiling_info, config=config)


def initialize(args, config, filename):
    sonar_model = args.sonar_model
    profile = args.profile
    export_csv = args.export_csv
    output_folder = args.output_folder

    config["raw_path"] = Path(filename)

    if profile is not None:
        config["profile"] = profile
    if export_csv is not None:
        config["export_csv"] = export_csv
    if sonar_model is not None:
        config["sonar_model"] = sonar_model
    if output_folder is not None:
        config["output_folder"] = output_folder


def create_enriched_sv(echodata, encode_mode, sv_dataset):
    sv_enriched = enrich_sv_dataset(
        sv_dataset, echodata, waveform_mode="CW", encode_mode=encode_mode
    )
    return sv_enriched


def main():
    args = parse_cli_arguments()

    # print(f"Processing file: {args.raw_data_source}")

    # logger = setup_logging(args.log_level, log_file=None)
    logging.info(f"Processing file: {args.raw_data_source}")

    # logging.basicConfig(level=logging_level, format='%(asctime)s - %(levelname)s - %(message)s', force=True)
    warnings.filterwarnings("ignore", category=UserWarning)

    data_source = args.raw_data_source

    if os.path.isfile(data_source):
        try:
            asyncio.run(process_file(data_source, args))
        except Exception as e:
            logging.exception(f"Error processing file {data_source}: {e}")
    else:
        print(f"The provided path '{data_source}' is not a valid file.")
        sys.exit(1)


if __name__ == "__main__":
    main()
