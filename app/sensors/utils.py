# Constants
sensor_output_range = 4096


# Inverse transformation functions
def bytes_to_measurement(
    bytes_value, measurement_range_min, measurement_range_width
):
    return (
        bytes_value / sensor_output_range
    ) * measurement_range_width + measurement_range_min


# ConduScm
measurement_range_min = 0
measurement_range_width = 1000 - measurement_range_min
valsorey_ts["ConduScm"] = bytes_to_measurement(
    valsorey_ts["Bytes_ConduScm"],
    measurement_range_min,
    measurement_range_width,
)

# DOmgL
measurement_range_min = 0
measurement_range_width = 20 - measurement_range_min
valsorey_ts["DOmgL"] = bytes_to_measurement(
    valsorey_ts["Bytes_DOmgL"], measurement_range_min, measurement_range_width
)

# CDOMppb
measurement_range_min = 0
measurement_range_width = 1250 - measurement_range_min
valsorey_ts["CDOMppb"] = bytes_to_measurement(
    valsorey_ts["Bytes_CDOMppb"],
    measurement_range_min,
    measurement_range_width,
)

# TurbiNTU
measurement_range_min = 0
measurement_range_width = 3000 - measurement_range_min
valsorey_ts["TurbiNTU"] = bytes_to_measurement(
    valsorey_ts["Bytes_TurbiNTU"],
    measurement_range_min,
    measurement_range_width,
)

# pCO2ppm
measurement_range_min = 0
measurement_range_width = 4000 - measurement_range_min
valsorey_ts["pCO2ppm"] = bytes_to_measurement(
    valsorey_ts["Bytes_pCO2ppm"],
    measurement_range_min,
    measurement_range_width,
)

# WDepthmm
measurement_range_min = 0
measurement_range_width = 1000 - measurement_range_min
valsorey_ts["WDepthmm"] = bytes_to_measurement(
    valsorey_ts["Bytes_WDepthmm"],
    measurement_range_min,
    measurement_range_width,
)

# WaterTempdegC
measurement_range_min = 0
measurement_range_width = 35 - measurement_range_min
valsorey_ts["WTempdegC"] = bytes_to_measurement(
    valsorey_ts["Bytes_WTempdegC"],
    measurement_range_min,
    measurement_range_width,
)

# BPhPa
measurement_range_min = 800
measurement_range_width = 1100 - measurement_range_min
valsorey_ts["BPhPa"] = bytes_to_measurement(
    valsorey_ts["Bytes_BPhPa"], measurement_range_min, measurement_range_width
)

# CO2ppm
measurement_range_min = 0
measurement_range_width = 4000 - measurement_range_min
valsorey_ts["CO2ppm"] = bytes_to_measurement(
    valsorey_ts["Bytes_CO2ppm"], measurement_range_min, measurement_range_width
)

# PARLux
measurement_range_min = 0
measurement_range_width = 320000 - measurement_range_min
valsorey_ts["PARLux"] = bytes_to_measurement(
    valsorey_ts["Bytes_PARLux"], measurement_range_min, measurement_range_width
)
