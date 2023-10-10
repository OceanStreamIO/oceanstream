from oceanstream.utils import dict_to_formatted_list


def test_dict_to_formatted_list():
    # Define a sample dictionary
    sample_dict = {
        "m": 5,
        "n": 20,
        "operation": "percentile15",
    }

    # Expected output
    expected_output = ["m=5", "n=20", "operation=percentile15"]

    # Call the function
    result = dict_to_formatted_list(sample_dict)

    # Assert that the result matches the expected output
    assert result == expected_output
