import ftplib
import os
from ftplib import FTP
from pathlib import Path

import echopype as ep
import pytest
from xarray import Dataset

from oceanstream.L2_calibrated_data.background_noise_remover import apply_remove_background_noise
from oceanstream.L2_calibrated_data.sv_computation import compute_sv
from oceanstream.L2_calibrated_data.sv_dataset_extension import enrich_sv_dataset

current_directory = os.path.dirname(os.path.abspath(__file__))
TEST_DATA_FOLDER = os.path.join(current_directory, "..", "test_data")
FTP_MAIN = "ftp.bas.ac.uk"
FTP_PARTIAL_PATH = "rapidkrill/ek60/"


def download_ftp_directory(ftp, remote_path, local_path):
    try:
        os.makedirs(local_path, exist_ok=True)
        items = ftp.nlst(remote_path)

        for item in items:
            local_item_path = os.path.join(local_path, os.path.basename(item))
            if is_directory(ftp, item):
                download_ftp_directory(ftp, item, local_item_path)
            else:
                # Check if the file already exists locally
                if not os.path.exists(local_item_path):
                    with open(local_item_path, "wb") as local_file:
                        ftp.retrbinary("RETR " + item, local_file.write)
                else:
                    continue

    except Exception as e:
        print(f"Error downloading {remote_path}. Error: {e}")


def download_ftp_file(ftp, remote_path, file_name, local_path):
    # Construct the full paths
    remote_file_path = os.path.join(remote_path, file_name)
    local_file_path = os.path.join(local_path, file_name)

    try:
        # Ensure the local directory exists
        os.makedirs(local_path, exist_ok=True)

        # Check if the file already exists locally
        if not os.path.exists(local_file_path):
            with open(local_file_path, "wb") as local_file:
                ftp.retrbinary("RETR " + remote_file_path, local_file.write)
        else:
            print(f"File {local_file_path} already exists. Skipping download.")

    except Exception as e:
        print(f"Error downloading {remote_file_path}. Error: {e}")


def is_directory(ftp, name):
    try:
        current = ftp.pwd()
        ftp.cwd(name)
        ftp.cwd(current)
        return True
    except ftplib.error_perm:
        return False


def ftp_raw_file_path(file_name):
    with FTP(FTP_MAIN) as ftp:
        ftp.login()  # Add credentials if needed: ftp.login(user="username", passwd="password")
        download_ftp_file(ftp, FTP_PARTIAL_PATH, file_name, TEST_DATA_FOLDER)
    local_path = os.path.join(TEST_DATA_FOLDER, file_name)
    return local_path


def get_sv_dataset(file_path, enriched: bool = False, waveform: str = "CW", encode: str = "power"):
    print(file_path)
    ed = ep.open_raw(file_path, sonar_model="ek60")  # type: ignore
    Sv = ep.calibrate.compute_Sv(ed).compute()
    if enriched is True:
        Sv = ep.consolidate.add_splitbeam_angle(Sv, ed, waveform, encode)
    return Sv


def get_raw_dataset(file_path):
    ed = ep.open_raw(file_path, sonar_model="ek60")  # type: ignore
    return ed


@pytest.fixture(scope="session")
def ftp_data():
    test_data_folder = Path(TEST_DATA_FOLDER) / "ek60"
    with FTP(FTP_MAIN) as ftp:
        ftp.login()  # Add credentials if needed: ftp.login(user="username", passwd="password")
        download_ftp_directory(ftp, FTP_PARTIAL_PATH, test_data_folder)
    yield str(test_data_folder)
    # Optional: Cleanup after tests are done
    # shutil.rmtree(TEST_DATA_FOLDER)


@pytest.fixture(scope="session")
def setup_test_data_jr230():
    file_name = "JR230-D20091215-T121917.raw"
    return ftp_raw_file_path(file_name)


@pytest.fixture(scope="session")
def setup_test_data_jr161():
    file_name = "JR161-D20061118-T010645.raw"
    return ftp_raw_file_path(file_name)


@pytest.fixture(scope="session")
def setup_test_data_jr179():
    file_name = "JR179-D20080410-T150637.raw"
    return ftp_raw_file_path(file_name)


@pytest.fixture(scope="session")
def sv_dataset_jr230(setup_test_data_jr230) -> Dataset:
    return get_sv_dataset(setup_test_data_jr230)


@pytest.fixture(scope="session")
def sv_dataset_jr161(setup_test_data_jr161) -> Dataset:
    return get_sv_dataset(setup_test_data_jr161)


@pytest.fixture(scope="session")
def sv_dataset_jr179(setup_test_data_jr179) -> Dataset:
    return get_sv_dataset(setup_test_data_jr179)


@pytest.fixture(scope="session")
def complete_dataset_jr179(setup_test_data_jr179):
    sv = get_sv_dataset(setup_test_data_jr179, enriched=True, waveform="CW", encode="power")
    return sv


@pytest.fixture(scope="session")
def raw_dataset_jr179(setup_test_data_jr179):
    ed = get_raw_dataset(setup_test_data_jr179)
    return ed


@pytest.fixture(scope="session")
def raw_dataset_jr230(setup_test_data_jr230):
    ed = get_raw_dataset(setup_test_data_jr230)
    return ed


@pytest.fixture(scope="session")
def ed_ek_60_for_Sv():
    bucket = "ncei-wcsd-archive"
    base_path = "data/raw/Bell_M._Shimada/SH1707/EK60/"
    filename = "Summer2017-D20170620-T011027.raw"
    rawdirpath = base_path + filename

    s3raw_fpath = f"s3://{bucket}/{rawdirpath}"
    storage_opts = {"anon": True}
    ed = ep.open_raw(s3raw_fpath, sonar_model="EK60", storage_options=storage_opts)  # type: ignore
    return ed


@pytest.fixture(scope="session")
def enriched_ek60_Sv(ed_ek_60_for_Sv):
    sv_echopype_EK60 = compute_sv(ed_ek_60_for_Sv)
    enriched_Sv = enrich_sv_dataset(
        sv=sv_echopype_EK60, echodata=ed_ek_60_for_Sv, waveform_mode="CW", encode_mode="power"
    )
    return enriched_Sv


# Read test raw data EK80
@pytest.fixture(scope="session")
def ed_ek_80_for_Sv():
    base_url = "noaa-wcsd-pds.s3.amazonaws.com/"
    path = "data/raw/Sally_Ride/SR1611/EK80/"
    file_name = "D20161109-T163350.raw"
    raw_file_address = base_url + path + file_name

    rf = raw_file_address  # Path(raw_file_address)
    ed_EK80 = ep.open_raw(
        f"https://{rf}",
        sonar_model="EK80",
    )
    return ed_EK80


@pytest.fixture(scope="session")
def ek_60_Sv_denoised(enriched_ek60_Sv):
    ds_Sv = apply_remove_background_noise(enriched_ek60_Sv)
    return ds_Sv


def test_transient(sv_dataset_jr161):
    source_Sv = sv_dataset_jr161
    print(source_Sv)
