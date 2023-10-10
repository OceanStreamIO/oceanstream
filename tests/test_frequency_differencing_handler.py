import echopype as ep
import numpy as np
import pytest

from oceanstream.L2_calibrated_data.background_noise_remover import apply_remove_background_noise
from oceanstream.L2_calibrated_data.sv_computation import compute_sv
from oceanstream.L3_regridded_data.frequency_differencing_handler import (
    find_mask_freq_diff,
    identify_fluid_like_organisms,
    identify_gas_bearing_organisms,
    identify_krill,
)


def test_apply_freq_diff(ed_ek_60_for_Sv):
    sv_echopype_EK60 = compute_sv(ed_ek_60_for_Sv)
    ds_Sv = apply_remove_background_noise(sv_echopype_EK60)
    chanA = "GPT 120 kHz 00907205a6d0 4-1 ES120-7C"
    chanB = "GPT  38 kHz 009072058146 2-1 ES38B"
    ds_Sv_interval_mask = find_mask_freq_diff(
        ds=ds_Sv,
        chanA=chanA,
        chanB=chanB,
        interval_start_operator=">=",
        interval_start_value="2.0",
        interval_end_operator="<=",
        interval_end_value="16.0",
    )
    ds_Sv_single_mask = find_mask_freq_diff(
        ds=ds_Sv, chanA=chanA, chanB=chanB, single_operator=">=", single_value="2.0"
    )
    ds_Sv_interval = ep.mask.apply_mask(ds_Sv, ds_Sv_interval_mask)
    ds_Sv_single = ep.mask.apply_mask(ds_Sv, ds_Sv_single_mask)
    assert np.nanmean(ds_Sv_interval["Sv"].values) == pytest.approx(-72.54676167765183, 0.0001)
    assert np.nanmin(ds_Sv_single["Sv"].values) == pytest.approx(-140.24009439945064, 0.0001)
    try:
        find_mask_freq_diff(ds=ds_Sv, chanA=chanA, chanB=chanB)
    except ValueError:
        pass


def test_identify_krill(ed_ek_60_for_Sv):
    sv_echopype_EK60 = compute_sv(ed_ek_60_for_Sv)
    ds_Sv = apply_remove_background_noise(sv_echopype_EK60)
    chan120 = "GPT 120 kHz 00907205a6d0 4-1 ES120-7C"
    chan38 = "GPT  38 kHz 009072058146 2-1 ES38B"
    ds_Sv_krill = identify_krill(ds_Sv, chan120=chan120, chan38=chan38)
    ds_Sv_krill = ep.mask.apply_mask(ds_Sv, ds_Sv_krill['mask_krill'])
    assert np.nanmax(ds_Sv_krill["Sv"].values) == pytest.approx(9.261225161665275, 0.0001)
    assert np.nanmean(ds_Sv_krill["Sv"].values) == pytest.approx(-72.54676167765183, 0.0001)


def test_identify_gas_bearing_organisms(ed_ek_60_for_Sv):
    sv_echopype_EK60 = compute_sv(ed_ek_60_for_Sv)
    ds_Sv = apply_remove_background_noise(sv_echopype_EK60)
    chan120 = "GPT 120 kHz 00907205a6d0 4-1 ES120-7C"
    chan38 = "GPT  38 kHz 009072058146 2-1 ES38B"
    ds_Sv_gas_bearing_organisms = identify_gas_bearing_organisms(
        ds_Sv, chan120=chan120, chan38=chan38
    )
    ds_Sv_gas_bearing_organisms = ep.mask.apply_mask(ds_Sv, ds_Sv_gas_bearing_organisms['mask_gas_bearing_organisms'])
    assert np.nanmean(ds_Sv_gas_bearing_organisms["Sv"].values) == pytest.approx(
        -69.26132957243746, 0.0001
    )


def test_identify_fluid_like_organisms(ed_ek_60_for_Sv):
    sv_echopype_EK60 = compute_sv(ed_ek_60_for_Sv)
    ds_Sv = apply_remove_background_noise(sv_echopype_EK60)
    chan120 = "GPT 120 kHz 00907205a6d0 4-1 ES120-7C"
    chan38 = "GPT  38 kHz 009072058146 2-1 ES38B"
    ds_Sv_fluid_like_organisms = identify_fluid_like_organisms(
        ds_Sv, chan120=chan120, chan38=chan38
    )
    ds_Sv_fluid_like_organisms = ep.mask.apply_mask(ds_Sv, ds_Sv_fluid_like_organisms['mask_fluid_like_organisms'])
    assert np.nanmean(ds_Sv_fluid_like_organisms["Sv"].values) == pytest.approx(
        -72.91705783069554, 0.0001
    )
