from typing import Union

from echopype.echodata import EchoData

from oceanstream.report import end_profiling, start_profiling

from .ensure_time_continuity import check_reversed_time, fix_time_reversions
from .raw_handler import file_integrity_checking, read_raw_files


def read_file(config, profiling_info=None) -> Union[dict[str, str], tuple[EchoData, str]]:
    start_time = None
    start_cpu = None
    start_memory = None

    if config["profile"]:
        start_time, start_cpu, start_memory = start_profiling()

    filename = config["raw_path"]
    check, file_integrity, encode_mode = check_file_integrity(
        filename, sonar_model=config["sonar_model"]
    )

    if not file_integrity:
        return {"Processing Error": f"File {filename} could not usable!"}

    echodata = read_raw_files([check])[0]
    if config["sonar_model"] == "EK80":
        encode_mode = get_encode_mode(echodata)

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


def get_encode_mode(echo_data: EchoData) -> str:
    """
    For EK80:
    If only complex data (can be BB or CW signals) exist,
    there exists only Beam_group1 and this group may
    contain CW or BB complex data, or a mixture of both. See example below.

    If only power/angle data (only valid for CW signals) exist,
    there exists only Beam_group1 and this group contains CW power and angle data.
    The structure is almost identical with EK60 data above.

    If both complex and power/angle data exist,
    there exist Beam_group1 (containing complex data)
    and Beam_group2 (containing power/angle data).
    """
    beam_group1, beam_group2 = check_beam_groups(echo_data)
    encode_mode = "power"
    if beam_group1:
        imaginary_part = "backscatter_i" in echo_data.data_vars
        if not imaginary_part:
            return "power"
        else:
            return "complex"
    if beam_group2:
        return "complex"
    return encode_mode


def check_beam_groups(echo_data: EchoData):
    # Check if the 'Sonar' group exists
    if "sonar" in echo_data.group_map:
        sonar_group = echo_data.group_map["sonar"]
        # Checking for Beam_group1 and Beam_group2
        has_beam_group1 = "Beam_group1" in sonar_group
        has_beam_group2 = "Beam_group2" in sonar_group

        return has_beam_group1, has_beam_group2
    else:
        # The 'Sonar' group does not exist in group_map
        return False, False
