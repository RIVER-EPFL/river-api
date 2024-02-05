from app.sensors.utils import SensorMeasurement
import pytest


def test_conversion_from_bytes(
    sensor_data_6h: list[dict[str, str]],
):

    # First compile a dictionary of values for each sensor
    sensors = {}
    for row in sensor_data_6h:
        for key, value in row.items():
            # Split column into {Property}_{Name}, eg. Bytes_DOmgL
            split_column = key.split("_")

            if key == "Date":
                continue
            if len(split_column) == 1:  # No prefix,
                name = split_column[0]
                property = "value"  # The value of the sensor
                sensors[name] = {}  # Set up disctionary of values for sensor
            else:
                property, name = split_column

            sensors[name][property] = value

    # Then for each sensor, test the conversion from bytes to measurement
    for sensor, values in sensors.items():
        # print(sensor)
        print(values)
        sensor_obj = SensorMeasurement(
            int(values["Min"]),
            int(values["Max"]),
        )
        conversion = sensor_obj.bytes_to_measurement(int(values["Bytes"]))
        print(sensor, conversion, values["value"])
        assert pytest.approx(conversion, 1.0) == float(values["value"])


# # ConduScm
# measurement_range_min = 0
# measurement_range_width = 1000 - measurement_range_min
# valsorey_ts["ConduScm"] = bytes_to_measurement(
#     valsorey_ts["Bytes_ConduScm"],
#     measurement_range_min,
#     measurement_range_width,
# )

# # DOmgL
# measurement_range_min = 0
# measurement_range_width = 20 - measurement_range_min
# valsorey_ts["DOmgL"] = bytes_to_measurement(
#     valsorey_ts["Bytes_DOmgL"], measurement_range_min, measurement_range_width
# )

# # CDOMppb
# measurement_range_min = 0
# measurement_range_width = 1250 - measurement_range_min
# valsorey_ts["CDOMppb"] = bytes_to_measurement(
#     valsorey_ts["Bytes_CDOMppb"],
#     measurement_range_min,
#     measurement_range_width,
# )

# # TurbiNTU
# measurement_range_min = 0
# measurement_range_width = 3000 - measurement_range_min
# valsorey_ts["TurbiNTU"] = bytes_to_measurement(
#     valsorey_ts["Bytes_TurbiNTU"],
#     measurement_range_min,
#     measurement_range_width,
# )

# # pCO2ppm
# measurement_range_min = 0
# measurement_range_width = 4000 - measurement_range_min
# valsorey_ts["pCO2ppm"] = bytes_to_measurement(
#     valsorey_ts["Bytes_pCO2ppm"],
#     measurement_range_min,
#     measurement_range_width,
# )

# # WDepthmm
# measurement_range_min = 0
# measurement_range_width = 1000 - measurement_range_min
# valsorey_ts["WDepthmm"] = bytes_to_measurement(
#     valsorey_ts["Bytes_WDepthmm"],
#     measurement_range_min,
#     measurement_range_width,
# )

# # WaterTempdegC
# measurement_range_min = 0
# measurement_range_width = 35 - measurement_range_min
# valsorey_ts["WTempdegC"] = bytes_to_measurement(
#     valsorey_ts["Bytes_WTempdegC"],
#     measurement_range_min,
#     measurement_range_width,
# )

# # BPhPa
# measurement_range_min = 800
# measurement_range_width = 1100 - measurement_range_min
# valsorey_ts["BPhPa"] = bytes_to_measurement(
#     valsorey_ts["Bytes_BPhPa"], measurement_range_min, measurement_range_width
# )

# # CO2ppm
# measurement_range_min = 0
# measurement_range_width = 4000 - measurement_range_min
# valsorey_ts["CO2ppm"] = bytes_to_measurement(
#     valsorey_ts["Bytes_CO2ppm"], measurement_range_min, measurement_range_width
# )

# # PARLux
# measurement_range_min = 0
# measurement_range_width = 320000 - measurement_range_min
# valsorey_ts["PARLux"] = bytes_to_measurement(
#     valsorey_ts["Bytes_PARLux"], measurement_range_min, measurement_range_width
# )
