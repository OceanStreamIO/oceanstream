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


def test_mask_metadata(complete_dataset_jr179, metadata=None):
    if metadata is None:
        metadata = {"test": "test"}
    source_Sv = complete_dataset_jr179
    mask = create_seabed_mask(source_Sv)
    mask_with_metadata = add_metadata_to_mask(mask, metadata)
    for k, v in metadata.items():
        assert mask_with_metadata.attrs[k] == v


def test_add_mask(complete_dataset_jr179, metadata=None):
    if metadata is None:
        metadata = {"mask_type": "seabed"}
    source_Sv = complete_dataset_jr179
    mask = create_seabed_mask(source_Sv)
    mask_metadata = add_metadata_to_mask(mask, metadata)
    Sv_mask = attach_mask_to_dataset(source_Sv, mask)
    for k, v in metadata.items():
        assert Sv_mask["mask_seabed"].attrs[k] == v
    assert Sv_mask["mask_seabed"].attrs["mask_type"]


def test_add_masks_rapidkrill(complete_dataset_jr179):
    source_Sv = complete_dataset_jr179
    Sv_mask = create_noise_masks_rapidkrill(source_Sv)
    assert Sv_mask["mask_seabed"].attrs["mask_type"] == "seabed"