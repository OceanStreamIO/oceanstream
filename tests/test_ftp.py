from pathlib import Path
import os
import re

import pytest
import xarray as xr

# from tests.conftest import *
from tests.conftest import TEST_DATA_FOLDER


def test_ftp_161(setup_test_data_jr161):
    assert os.path.isfile(setup_test_data_jr161)
    
def test_ftp_230(setup_test_data_jr230):

    assert os.path.isfile(setup_test_data_jr230)

def test_ftp_179(setup_test_data_jr179):
    assert os.path.isfile(setup_test_data_jr179)

