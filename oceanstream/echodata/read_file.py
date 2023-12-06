from typing import Union
from echopype.echodata import EchoData

from oceanstream.report import start_profiling, end_profiling
from .raw_handler import file_integrity_checking
from .raw_handler import read_raw_files
from .ensure_time_continuity import fix_time_reversions, check_reversed_time


def read_file(config, profiling_info=None) -> Union[dict[str, str], tuple[EchoData, str]]:
    start_time = None
    start_cpu = None
    start_memory = None

    if config["profile"]:
        start_time, start_cpu, start_memory = start_profiling()

    filename = config["raw_path"]
    check, file_integrity, encode_mode = check_file_integrity(filename, sonar_model=config["sonar_model"])

    if not file_integrity:
        return {"Processing Error": f"File {filename} could not usable!"}

    echodata = read_raw_files([check])[0]

    # Fix time reversions if necessary
    if check_reversed_time(echodata, "Sonar/Beam_group1", "ping_time"):
        echodata = fix_time_reversions(echodata, {"Sonar/Beam_group1": "ping_time"})

    if config["profile"]:
        profiling_info["read file"] = end_profiling(start_time, start_cpu, start_memory)

    return echodata, encode_mode


def check_file_integrity(filename, sonar_model: str = None):
    check = file_integrity_checking(filename)

    if sonar_model == "EK80":
        encode_mode = "complex"
    else:
        encode_mode = "power"
    check["sonar_model"] = sonar_model

    return check, check.get("file_integrity", False), encode_mode
