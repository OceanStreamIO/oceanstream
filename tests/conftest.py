import os
from ftplib import FTP

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