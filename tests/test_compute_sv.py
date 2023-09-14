from pathlib import Path

import echopype as ep
import pytest
from pydantic import ValidationError

from oceanstream.L2_calibrated_data.compute_sv import (
    ComputeSVParams,
    SupportedSonarModelsForSv,
)


# Read test raw data EK60
def _read_EK60_test_data():
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
def _read_EK80_test_data():
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


def test_valid_sonar_models():
    assert SupportedSonarModelsForSv("EK60") == SupportedSonarModelsForSv.EK60
    assert SupportedSonarModelsForSv("AZFP") == SupportedSonarModelsForSv.AZFP
    assert SupportedSonarModelsForSv("EK80") == SupportedSonarModelsForSv.EK80


def test_invalid_sonar_model():
    with pytest.raises(ValueError):
        SupportedSonarModelsForSv("INVALID_MODEL")

    with pytest.raises(ValueError):
        SupportedSonarModelsForSv("EK90")


def test_invalid_echodata_type():
    # Test with invalid echodata
    with pytest.raises(ValidationError):
        ComputeSVParams(echodata={"sonar_model": "dummy"})


ed_ek_60 = _read_EK60_test_data()
ed_ek_80 = _read_EK80_test_data()


@pytest.mark.parametrize("ed", [ed_ek_60, ed_ek_80])
def test_waveform_mode_validity_for_ek80(ed):
    # Using sonar model from real echodata
    if ed.sonar_model == "EK80":
        # This should pass
        ComputeSVParams(echodata=ed, waveform_mode="CW")
    else:
        # This should raise ValidationError
        # since waveform_mode is only valid for EK80
        with pytest.raises(ValidationError):
            ComputeSVParams(echodata=ed, waveform_mode="CW")


@pytest.mark.parametrize("ed", [ed_ek_60, ed_ek_80])
def test_encode_mode_validator(ed):
    # Using sonar model from real echodata
    if ed.sonar_model == "EK80":
        # This should pass
        ComputeSVParams(echodata=ed, encode_mode="complex")
    else:
        # This should raise ValidationError since encode_mode
        # is only valid for EK80
        with pytest.raises(ValidationError):
            ComputeSVParams(echodata=ed, encode_mode="complex")


@pytest.mark.parametrize("ed", [ed_ek_60, ed_ek_80])
def test_env_params(ed):
    # Test with typical env_params
    env_params = {"temperature": "20"}
    model = ComputeSVParams(echodata=ed, env_params=env_params)
    assert model.env_params == env_params

    # Test with missing or None env_params
    model = ComputeSVParams(echodata=ed, env_params=None)
    assert model.env_params is None

    # Test with incorrect env_params
    with pytest.raises(ValueError):
        ComputeSVParams(echodata=ed, env_params="incorrect_value")


@pytest.mark.parametrize("ed", [ed_ek_60, ed_ek_80])
def test_cal_params(ed):
    # Test with typical cal_params
    cal_params = {"gain_correction": "0.5"}
    model = ComputeSVParams(echodata=ed, cal_params=cal_params)
    assert model.cal_params == cal_params

    # Test with missing or None cal_params
    model = ComputeSVParams(echodata=ed, cal_params=None)
    assert model.cal_params is None

    # Test with incorrect cal_params
    with pytest.raises(ValueError):
        ComputeSVParams(echodata=ed, cal_params="incorrect_value")
