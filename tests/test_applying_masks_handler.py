import numpy as np
import pytest

from oceanstream.L2_calibrated_data.noise_masks import create_default_noise_masks_oceanstream
from oceanstream.L3_regridded_data import frequency_differencing_handler, shoal_detection_handler
from oceanstream.L3_regridded_data.applying_masks_handler import (
    apply_mask_organisms_in_order,
    apply_selected_noise_masks_and_or_noise_removal,
)


def test_apply_selected_noise_masks_and_or_noise_removal(enriched_ek60_Sv):
    enriched_Sv = enriched_ek60_Sv
    Sv_with_masks = create_default_noise_masks_oceanstream(enriched_Sv)

    process_parameters = {
        "mask_transient": {
            "var_name": "Sv",
        },
        "mask_impulse": {
            "var_name": "Sv",
        },
        "mask_attenuation": {
            "var_name": "Sv",
        },
        "remove_background_noise": {
            "ping_num": 40,
            "range_sample_num": 10,
            "noise_max": -125,
            "SNR_threshold": 3,
        },
    }
    ds_processed = apply_selected_noise_masks_and_or_noise_removal(
        Sv_with_masks, process_parameters
    )
    assert np.nanmean(ds_processed["Sv"].values) == pytest.approx(-77.02628114845355, 0.0001)
    with pytest.raises(ValueError, match="Unexpected mask/process"):
        apply_selected_noise_masks_and_or_noise_removal(Sv_with_masks, "invalid_parameters")

@pytest.mark.ignore
def test_apply_mask_organisms_in_order(enriched_ek60_Sv):
    enriched_Sv = enriched_ek60_Sv

    chan120 = "GPT 120 kHz 00907205a6d0 4-1 ES120-7C"
    chan38 = "GPT  38 kHz 009072058146 2-1 ES38B"
    ds_Sv_with_krill_mask = frequency_differencing_handler.identify_krill(
        enriched_Sv, chan120=chan120, chan38=chan38
    )
    ds_Sv_with_shoal_combined_mask = shoal_detection_handler.attach_shoal_mask_to_ds(
        ds_Sv_with_krill_mask
    )

    process_parameters = {
        "mask_krill": {
            "var_name": "Sv",
        },
        "mask_shoal": {
            "var_name": "Sv",
        },
    }

    ds_processed = apply_mask_organisms_in_order(ds_Sv_with_shoal_combined_mask, process_parameters)
    assert np.nanmean(ds_processed["Sv"].values) == pytest.approx(-56.85248587691882, 0.0001)
    with pytest.raises(ValueError, match="Unexpected mask"):
        apply_selected_noise_masks_and_or_noise_removal(ds_processed, "invalid_parameters")
