from oceanstream.utils import tfc
from oceanstream.L2_calibrated_data.background_noise_remover import apply_remove_background_noise
from oceanstream.L2_calibrated_data.sv_computation import compute_sv

from oceanstream.L3_regridded_data.shoal_detection_handler import attach_shoal_mask_to_ds
from oceanstream.L3_regridded_data.shoal_process import *

def prep_dataset(Sv):
    # fix this once we update shoal
    parameters = {"thr": -55, "maxvgap": -5, "maxhgap": 0, "minvlen": 5, "minhlen": 5}
    shoal_dataset = attach_shoal_mask_to_ds(Sv, parameters=parameters, method="will")
    shoal_dataset["mask_shoal"][:,: ,0:25] = False
    shoal_dataset["mask_shoal"][:,: ,600:] = False
    shoal_dataset["mask_shoal"][:,0:600 ,:] = False
    shoal_dataset["mask_shoal"][:,800: ,:] = False
    # shoal_dataset = enrich_sv_dataset(shoal_dataset, raw, depth_offset=200, waveform_mode="CW", encode_mode="power")
    return shoal_dataset

def test_split_shoal(ek_60_Sv_denoised):
    expected_results = [(10362, 6104418), (11155, 6103625), (44, 6114736),
                        (21, 6114759), (21, 6114759), (20, 6114760)]
    shoal_dataset = prep_dataset(ek_60_Sv_denoised)
    res = split_shoal_mask(shoal_dataset)
    res_tfc = [tfc(r) for r in res]
    assert res_tfc == expected_results

