# Constants
from app.config import constants


class SensorMeasurement:
    def __init__(
        self,
        range_min: int,
        range_max: int,
        output_range: int = constants.DEFAULT_SENSOR_OUTPUT_RANGE,
        unit: str | None = None,
    ):
        """
        range_min : int
            The minimum value of the measurement range
        range_max : int
            The width of the measurement range
        """

        self.range_min = range_min
        self.range_width = range_max - range_min
        self.unit = unit
        self.output_range = output_range

    def __str__(
        self,
        value: float,
    ):
        if self.unit is None:
            return str(value)
        return f"{value} {self.unit}"

    def bytes_to_measurement(
        self,
        bytes_value: int,
    ):
        """Inverse transformation function

        Converts a byte value to a measurement value

        Parameters
        ----------
        bytes_value : int
            The byte value to be converted


        Returns
        -------
        float
            The measurement value
        """
        return (
            bytes_value / self.output_range
        ) * self.range_width + self.range_min
