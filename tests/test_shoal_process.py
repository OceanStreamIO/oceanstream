from oceanstream.utils import tfc
from oceanstream.L3_regridded_data.shoal_detection_handler import attach_shoal_mask_to_ds
from oceanstream.L3_regridded_data.shoal_process import *



def prep_dataset(Sv):
    parameters = {"thr": -55, "maxvgap": -5, "maxhgap": 0, "minvlen": 5, "minhlen": 5}
    shoal_dataset = attach_shoal_mask_to_ds(Sv, parameters=parameters, method="will")
    shoal_dataset["mask_shoal"][:,: ,0:25] = False
    shoal_dataset["mask_shoal"][:,: ,600:] = False
    shoal_dataset["mask_shoal"][:,0:600 ,:] = False
    shoal_dataset["mask_shoal"][:,800: ,:] = False
    return shoal_dataset


def test_split_shoal(ek_60_Sv_denoised):
    expected_results = [(10362, 6104418), (11155, 6103625), (44, 6114736),
                        (21, 6114759), (21, 6114759), (20, 6114760)]
    shoal_dataset = prep_dataset(ek_60_Sv_denoised)
    res = split_shoal_mask(shoal_dataset)
    res_tfc = [tfc(r) for r in res]
    assert res_tfc == expected_results


def test_single_shoal(ek_60_Sv_denoised):
    shoal_dataset = prep_dataset(ek_60_Sv_denoised)
    mask = split_shoal_mask(shoal_dataset)[0]
    res = process_single_shoal(shoal_dataset, mask)
    assert len(res) == 3
    assert len(res[0]) == 23
    assert res[0]["area"] == 4252


def test_shoals(ek_60_Sv_denoised):
    shoal_dataset = prep_dataset(ek_60_Sv_denoised)
    res = process_shoals(shoal_dataset)
    none_res = [r for r in res if r is None]
    assert len(res) == 10
    assert len(none_res) == 0


