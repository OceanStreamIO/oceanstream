import pytest

from oceanstream.L2_calibrated_data import sv_interpolation
from oceanstream.L2_calibrated_data.noise_masks import create_default_noise_masks_oceanstream
from oceanstream.L3_regridded_data import applying_masks_handler, nasc_computation


def test_compute_per_dataset_nasc(enriched_ek60_Sv):
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
    }
    cleaned_ds = applying_masks_handler.apply_selected_noise_masks_and_or_noise_removal(
        Sv_with_masks,
        process_parameters,
    )
    interpolated_ds = sv_interpolation.interpolate_sv(cleaned_ds)
    interpolated_ds = interpolated_ds.rename({"Sv": "Sv_denoised", "Sv_interpolated": "Sv"})
    process_parameters = {
        "remove_background_noise": {
            "ping_num": 40,
            "range_sample_num": 10,
            "noise_max": -125,
            "SNR_threshold": 3,
        },
    }
    interpolated_ds = applying_masks_handler.apply_selected_noise_masks_and_or_noise_removal(
        interpolated_ds, process_parameters
    )

    nasc_os = nasc_computation.compute_per_dataset_nasc(interpolated_ds)

    val = (
        nasc_os["NASC_dataset"]["NASC"]
        .sel(channel="GPT  18 kHz 009072058c8d 1-1 ES18-11")
        .values[0][0]
    )
    assert val == pytest.approx(31774234.87447954, 0.0001)
    assert nasc_os["maximum_depth"][0:3] == "199"
    assert nasc_os["maximum_distance"][0:3] == "3.2"
