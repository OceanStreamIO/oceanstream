# import pytest
# import xarray as xr

from oceanstream.L2_calibrated_data.noise_masks import *


def test_impulse(sv_dataset_jr230):
    source_Sv = sv_dataset_jr230
    mask = create_impulse_mask(source_Sv, method="ryan", thr=10, m=1, n=1)
    assert mask["channel"].shape == (3, )


def test_transient(sv_dataset_jr161):
    source_Sv = sv_dataset_jr161
    mask = create_transient_mask(source_Sv)
    assert mask["channel"].shape == (3, )
    

def test_attenuation(sv_dataset_jr161):
    source_Sv = sv_dataset_jr161
    mask = create_attenuation_mask(source_Sv)
    assert mask["channel"].shape == (3, )


def test_seabed(complete_dataset_jr179):
    source_Sv = complete_dataset_jr179
    mask = create_seabed_mask(source_Sv)
    assert mask["channel"].shape == (3, )


