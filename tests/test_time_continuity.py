import pytest

from oceanstream.L0_unprocessed_data.ensure_time_continuity import (
    check_reversed_time,
    fix_time_reversions,
)


@pytest.mark.parametrize(
    "dim, time", [("Sonar/Beam_group1", "ping_time")]
)
def test_check_reverse_time(raw_dataset_jr230, dim: str, time: str):
    dataset = raw_dataset_jr230
    has_reverse = check_reversed_time(dataset, dim, time)
    assert not has_reverse
    pings = dataset[dim].coords[time].values
    pings[51] = "2009-12-15T12:20:55.3130629021"
    has_reverse_bad = check_reversed_time(dataset, dim, time)
    #otherwise the session object stays modified
    dataset = fix_time_reversions(dataset, time_dict={dim: time})
    assert has_reverse_bad



@pytest.mark.parametrize(
    "dim, time", [("Sonar/Beam_group1", "ping_time")]
)
def test_fix_reversal(raw_dataset_jr230, dim: str, time: str):
    dataset = raw_dataset_jr230
    dataset[dim].coords[time].values[51] = "2009-12-15T12:20:55.3130629021"
    has_reverse_bad = check_reversed_time(dataset, dim, time)
    fixed_dataset = fix_time_reversions(dataset, time_dict={dim: time})
    has_reverse_fix = check_reversed_time(fixed_dataset, dim, time)
    assert has_reverse_bad
    assert not has_reverse_fix



