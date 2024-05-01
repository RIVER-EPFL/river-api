# from app.stations.utils import StationMeasurement
# import pytest


# def test_conversion_from_bytes(
#     sensor_data_6h: list[dict[str, str]],
# ):

#     sensors = {}
#     for i, row in enumerate(sensor_data_6h):
#         print(f"\nWorking on row {i}")
#         # First compile a dictionary of values for each sensor
#         for key, value in row.items():
#             # Split column into {Property}_{Name}, eg. Bytes_DOmgL
#             split_column = key.split("_")

#             if key == "Date":
#                 continue
#             if len(split_column) == 1:  # No prefix,
#                 name = split_column[0]
#                 property = "value"  # The value of the sensor
#                 sensors[name] = {}  # Set up disctionary of values for sensor
#             else:
#                 property, name = split_column

#             sensors[name][property] = value if value != "NaN" else None

#         # Then for each sensor, test the conversion from bytes to measurement
#         for sensor, values in sensors.items():
#             print(f"{sensor}: {values}")

#             # Define the sensor object
#             sensor_obj = StationMeasurement(
#                 int(values["Min"]),
#                 int(values["Max"]),
#             )

#             # Don't test in the case that the value is NaN (NoneType)
#             if values["value"] is None:
#                 continue

#             # Test exceptions where the byte value is outside the range
#             if (int(values["Bytes"]) < int(values["Min"])) or (
#                 int(values["Bytes"]) > int(values["Max"])
#                 or (values["value"] is None)
#             ):
#                 with pytest.raises(
#                     ValueError,
#                 ):
#                     conversion = sensor_obj.bytes_to_measurement(
#                         int(values["Bytes"])
#                     )
#                 continue

#             # Test the conversion
#             conversion = sensor_obj.bytes_to_measurement(int(values["Bytes"]))

#             # Assert the conversion converts within a threshold of 1.0
#             assert pytest.approx(conversion) == float(float(values["value"]))

from app.utils import get_unix_time_from_str, extract_raw_values_from_str
import datetime


def test_get_unix_time_from_str(
    data_message: tuple[str, list[int], datetime.datetime]
):
    """Test the conversion of a string to a unix timestamp"""
    data_string, expected_values, expected_time = data_message

    assert get_unix_time_from_str(data_string) == expected_time


def test_extract_raw_values_from_str(
    data_message: tuple[str, list[int], datetime.datetime]
):
    """Test the extraction of raw values from a string"""
    data_string, expected_values, expected_time = data_message

    assert extract_raw_values_from_str(data_string) == expected_values
