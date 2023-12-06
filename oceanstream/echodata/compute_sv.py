import xarray as xr
from echopype.echodata import EchoData

from oceanstream.report import end_profiling, start_profiling

from .sv_computation import compute_sv


def compute_sv_with_encode_mode(
    echodata: EchoData, encode_mode: str, config, profiling_info=None
) -> xr.Dataset:
    start_time = None
    start_cpu = None
    start_memory = None

    if config["profile"]:
        start_time, start_cpu, start_memory = start_profiling()

    if encode_mode == "power":
        sv_dataset = compute_sv(echodata)
    else:
        sv_dataset = compute_sv(echodata, waveform_mode="CW", encode_mode="power")

    if config["profile"]:
        profiling_info["compute sv"] = end_profiling(start_time, start_cpu, start_memory)

    return sv_dataset
