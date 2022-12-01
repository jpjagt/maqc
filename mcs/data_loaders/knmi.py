from mcs.constants import (
    KNMI_DATA_DIR,
    EXPERIMENT_START_DATE,
    EXPERIMENT_END_DATE,
)
import os
import pandas as pd

colcode2colname = {
    "# STN": "station",
    "YYYYMMDD": "date",
    "HH": "hour",
    "DD": "wind_direction",
    "FH": "wind_speed_hourly",
    "FF": "wind_speed_last10min",
    "FX": "wind_max_gust",
    "T": "temperature",
    "T10N": "temperature_min",
    "TD": "temperature_dew_point",
    "SQ": "sunshien_duration",
    "Q": "global_radiation",
    "DR": "precipitation_duration",
    "RH": "precipitation_hourly",
    "P": "air_pressure",
    "VV": "horizontal_visibility",
    "N": "cloud_cover",
    "U": "relative_humidity",
    "WW": "weather_code",
    "IX": "indicator_present_weather_code",
    "M": "is_foggy",
    "R": "is_raining",
    "S": "is_snowing",
    "O": "is_thundering",
    "Y": "ice_formation",
}

# old col names for hourly data:
# col_names = [
#     "Station",
#     "Date",
#     "Avg_Wind_Direction",
#     "Avg_Windspeed",
#     "Daily_Avg_Windspeed",
#     "Max_Windspeed",
#     "Time_Max_Windspeed",
#     "Min_Windspeed",
#     "Time_Min_Windspeed",
#     "Max_Gust",
#     "Time_Max_Gust",
#     "Avg_Temp",
#     "Min_Temp",
#     "Time_Min_Temp",
#     "Max_Temp",
#     "Time_Max_Temp",
#     "Min_Temp_10cm",
#     "Time_Min_Temp_10cm",
#     "Sun_Duration",
#     "Pct_Max_Sun",
#     "Radiation",
#     "Precip_Duration",
#     "Precip_Amt",
#     "Max_Precip",
#     "Time_Max_Precip",
#     "Avg_Sea_Pressure",
#     "Max_Sea_Pressure",
#     "Time_Max_Sea_Pressure",
#     "Min_Sea_Pressure",
#     "Time_Min_Sea_Pressure",
#     "Min_Visibility",
#     "Time_Min_Visibility",
#     "Max_Visibility",
#     "Time_Max_Visibility",
#     "Avg_Cloud_Cover",
#     "Avg_Atmos_Humidity",
#     "Max_Humidity",
#     "Time_Max_Humidity",
#     "Min_Humidity",
#     "Time_Min_Humidity",
#     "Evapotranspiration",
# ]


class KNMIDataLoader(object):
    def load_data(self):
        fname = "uurgeg_240_2021-2030.txt"
        fpath = os.path.join(KNMI_DATA_DIR, fname)
        df = pd.read_csv(fpath, skiprows=30, sep=",")
        df.columns = df.columns.str.strip().map(colcode2colname)

        # convert date and time information to DateTime column
        df["timestamp"] = pd.to_datetime(
            df["date"].astype(str)
            + " "
            + df["hour"].astype(str).str.zfill(2).replace("24", "00"),
            format="%Y%m%d %H",
        )

        # set timestamp as index
        df = df.set_index("timestamp")

        # only select data which was within experiment time period
        df = df.loc[EXPERIMENT_START_DATE:EXPERIMENT_END_DATE]

        return df
