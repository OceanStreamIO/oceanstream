from pathlib import Path
import os
import re

import pytest
import xarray as xr

# from tests.conftest import *
from tests.conftest import TEST_DATA_FOLDER

from oceanstream.L2_calibrated_data.noise_masks import *



def test_ftp(sv_dataset_jr161):
    source_Sv = sv_dataset_jr161
    print(source_Sv)
