import pytest
from pydantic import ValidationError

from oceanstream.echodata.sv_computation import ComputeSVParams, SupportedSonarModelsForSv


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
        ComputeSVParams(echodata={"sonar_model": "incorrect"})


def test_encode_mode_validity(ed_ek_60_for_Sv, ed_ek_80_for_Sv):
    for ed in [ed_ek_60_for_Sv, ed_ek_80_for_Sv]:
        # Using sonar model from real echodata
        # Testing with invalid encode_mode
        with pytest.raises(ValidationError):
            ComputeSVParams(echodata=ed, encode_mode="INVALID_MODE")
        # Testing with valid encode_mode values
        valid_encode_modes = ["complex", "power"]
        for mode in valid_encode_modes:
            # This should pass without raising any error
            ComputeSVParams(echodata=ed, encode_mode=mode)


def test_waveform_mode_validity(ed_ek_60_for_Sv, ed_ek_80_for_Sv):
    for ed in [ed_ek_60_for_Sv, ed_ek_80_for_Sv]:
        # Using sonar model from real echodata
        # Testing with invalid waveform_mode
        with pytest.raises(ValidationError):
            ComputeSVParams(echodata=ed, waveform_mode="INVALID_MODE")
        # Testing with valid waveform_mode values
        valid_waveform_modes = ["CW", "BB"]
        for mode in valid_waveform_modes:
            # This should pass without raising any error
            ComputeSVParams(echodata=ed, waveform_mode=mode)


def test_env_params(ed_ek_60_for_Sv, ed_ek_80_for_Sv):
    for ed in [ed_ek_60_for_Sv, ed_ek_80_for_Sv]:
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


def test_cal_params(ed_ek_60_for_Sv, ed_ek_80_for_Sv):
    for ed in [ed_ek_60_for_Sv, ed_ek_80_for_Sv]:
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
