from oceanstream.exports.shoals.shoals_handler import attach_shoal_mask_to_ds

from oceanstream.exports.shoals.shoal_process import (
    process_shoals,
    process_single_shoal,
    split_shoal_mask,
)
from oceanstream.utils import tfc

WEILL_DEFAULT_PARAMETERS = {
    "thr": -55,
    "maxvgap": 5,
    "maxhgap": 5,
    "minvlen": 5,
    "minhlen": 5,
    "dask_chunking": {"ping_time": 1000, "range_sample": 1000},
}

# @pytest.mark.ignore
def prep_dataset(Sv):
    parameters = WEILL_DEFAULT_PARAMETERS
    shoal_dataset = attach_shoal_mask_to_ds(Sv, parameters=parameters, method="will")
    shoal_dataset["mask_shoal"][:, :, 0:25] = False
    shoal_dataset["mask_shoal"][:, :, 600:] = False
    shoal_dataset["mask_shoal"][:, 0:600, :] = False
    shoal_dataset["mask_shoal"][:, 800:, :] = False
    return shoal_dataset

# @pytest.mark.ignore
def test_split_shoal(ek_60_Sv_denoised):
    expected_results = [(13671, 6101109), (13465, 6101315), (30, 6114750)]
    shoal_dataset = prep_dataset(ek_60_Sv_denoised)
    res = split_shoal_mask(shoal_dataset)
    res_tfc = [tfc(r) for r in res]
    assert res_tfc == expected_results

# @pytest.mark.ignore
def test_single_shoal(ek_60_Sv_denoised):
    shoal_dataset = prep_dataset(ek_60_Sv_denoised)
    mask = split_shoal_mask(shoal_dataset)[0]
    res = process_single_shoal(shoal_dataset, mask)
    assert len(res) == 3
    assert len(res[0]) == 24
    assert res[0]["area"] == 6017

# @pytest.mark.ignore
def test_shoals(ek_60_Sv_denoised):
    shoal_dataset = prep_dataset(ek_60_Sv_denoised)
    res = process_shoals(shoal_dataset)
    none_res = [r for r in res if r is None]
    assert len(res) == 7
    assert len(none_res) == 0
