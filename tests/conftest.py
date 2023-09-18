import os
from ftplib import FTP
from pathlib import Path

import echopype as ep
import pytest


current_directory = os.path.dirname(os.path.abspath(__file__))
TEST_DATA_FOLDER = os.path.join(current_directory, "..", "test_data", "ek60")

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
                    # print(f"File {local_item_path} already exists. Skipping download.")
                    continue

    except Exception as e:
        print(f"Error downloading {remote_path}. Error: {e}")


def is_directory(ftp, name):
    try:
        current = ftp.pwd()
        ftp.cwd(name)
        ftp.cwd(current)
        return True
    except:
        return False


@pytest.fixture(scope="session")
def ftp_data():
    with FTP(FTP_MAIN) as ftp:
        ftp.login()  # Add credentials if needed: ftp.login(user="username", passwd="password")
        download_ftp_directory(ftp, FTP_PARTIAL_PATH, TEST_DATA_FOLDER)
    yield TEST_DATA_FOLDER
    # Optional: Cleanup after tests are done
    # shutil.rmtree(TEST_DATA_FOLDER)


@pytest.fixture(scope="module")
def ed_ek_60_for_Sv():
    bucket = "ncei-wcsd-archive"
    base_path = "data/raw/Bell_M._Shimada/SH1707/EK60/"
    filename = "Summer2017-D20170620-T011027.raw"
    rawdirpath = base_path + filename

    s3raw_fpath = f"s3://{bucket}/{rawdirpath}"
    storage_opts = {"anon": True}
    ed = ep.open_raw(
        s3raw_fpath,
        sonar_model="EK60",
        storage_options=storage_opts
    )
    return ed


# Read test raw data EK80
@pytest.fixture(scope="module")
def ed_ek_80_for_Sv():
    base_url = "noaa-wcsd-pds.s3.amazonaws.com/"
    path = "data/raw/Sally_Ride/SR1611/EK80/"
    file_name = "D20161109-T163350.raw"
    raw_file_address = base_url + path + file_name

    rf = Path(raw_file_address)
    ed_EK80 = ep.open_raw(
        f"https://{rf}",
        sonar_model="EK80",
    )
    return ed_EK80
