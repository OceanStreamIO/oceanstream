import os
import subprocess
from pathlib import Path

import echopype as ep
import pytest

from oceanstream.L0_unprocessed_data.ensure_time_continuity \
    import check_reversed_time, fix_time_reversions

current_directory = os.path.dirname(os.path.abspath(__file__))
FTP_MAIN = "ftp.bas.ac.uk"
FTP_PARTIAL_PATH = "rapidkrill/ek60/"
BASE_FOLDER = Path(__file__).parent.parent.absolute()
TEST_DATA_FOLDER = BASE_FOLDER / "test_data"
FILE_NAME = "JR230-D20091215-T121917.raw"


def _setup_file(file_name):
    test_data_path = os.path.join(TEST_DATA_FOLDER, file_name)
    if not os.path.exists(TEST_DATA_FOLDER):
        os.mkdir(TEST_DATA_FOLDER)
    if not os.path.exists(test_data_path):
        ftp_file_path = FTP_MAIN + FTP_PARTIAL_PATH + file_name
        subprocess.run(["wget", ftp_file_path, "-o", test_data_path])
    ed = ep.open_raw(test_data_path, sonar_model="EK60")
    return ed


@pytest.mark.parametrize(
    "file_name, dim, time",
    [(FILE_NAME, "Sonar/Beam_group1", "ping_time")]
)
def test_check_reverse_time(file_name: str, dim: str, time: str):
    dataset = _setup_file(file_name)
    has_reverse = check_reversed_time(dataset, dim, time)
    assert not has_reverse
    pings = dataset[dim].coords[time].values
    pings[51] = "2009-12-15T12:20:55.3130629021"
    has_reverse_bad = check_reversed_time(dataset, dim, time)
    assert has_reverse_bad


@pytest.mark.parametrize(
    "file_name, dim, time",
    [(FILE_NAME, "Sonar/Beam_group1", "ping_time")]
)
def test_fix_reversal(file_name: str, dim: str, time: str):
    dataset = _setup_file(file_name)
    dataset[dim].coords[time].values[51] \
        = "2009-12-15T12:20:55.3130629021"
    fixed_dataset = fix_time_reversions(dataset, dim, time)
    has_reverse_bad = check_reversed_time(dataset, dim, time)
    has_reverse_fix = check_reversed_time(fixed_dataset, dim, time)
    assert has_reverse_bad
    assert not has_reverse_fix







