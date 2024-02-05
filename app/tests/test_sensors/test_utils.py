from app.sensors.utils import SensorMeasurement
import pytest


def test_conversion_from_bytes(
    sensor_data_6h: list[dict[str, str]],
):

    sensors = {}
    for i, row in enumerate(sensor_data_6h):
        print(f"Working on row {i}")
        # First compile a dictionary of values for each sensor
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

            sensors[name][property] = value if value != "NaN" else None

        # Then for each sensor, test the conversion from bytes to measurement
        for sensor, values in sensors.items():
            # print(sensor)
            print(f"{sensor}: {values}")
            sensor_obj = SensorMeasurement(
                int(values["Min"]),
                int(values["Max"]),
            )

            # Ignore values that are None
            if values["value"] is None:
                continue

            # Don't validate if the value is
            if (int(values["Bytes"]) < int(values["Min"])) or (
                int(values["Bytes"]) > int(values["Max"])
                or (values["value"] is None)
            ):
                with pytest.raises(
                    ValueError,
                ):
                    conversion = sensor_obj.bytes_to_measurement(
                        int(values["Bytes"])
                    )
                continue
            conversion = sensor_obj.bytes_to_measurement(int(values["Bytes"]))

            assert pytest.approx(conversion, 1.0) == float(
                float(values["value"])
            )
