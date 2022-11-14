from mcs.constants import KNMI_DATA_DIR
from mcs.constants import KNMI_START_DATE
import os
import pandas as pd


class KNMIDataLoader(object):
    def load_data(self):
        fpath = os.path.join(KNMI_DATA_DIR, "etmgeg_240.txt")
        with open(fpath, 'r') as f:
            df = pd.read_csv(f, skiprows=50, sep=",")
            df.columns = df.columns.str.strip()

        col_names = ["Station", "Date", "Avg_Wind_Direction", "Avg_Windspeed", "Daily_Avg_Windspeed", "Max_Windspeed",
                    "Time_Max_Windspeed", "Min_Windspeed", "Time_Min_Windspeed", "Max_Gust", "Time_Max_Gust",
                    "Avg_Temp", "Min_Temp", "Time_Min_Temp", "Max_Temp", "Time_Max_Temp", "Min_Temp_10cm", "Time_Min_Temp_10cm",
                    "Sun_Duration", "Pct_Max_Sun", "Radiation", "Precip_Duration", "Precip_Amt", "Max_Precip", "Time_Max_Precip",
                    "Avg_Sea_Pressure", "Max_Sea_Pressure", "Time_Max_Sea_Pressure", "Min_Sea_Pressure", "Time_Min_Sea_Pressure",
                    "Min_Visibility", "Time_Min_Visibility", "Max_Visibility", "Time_Max_Visibility", "Avg_Cloud_Cover",
                    "Avg_Atmos_Humidity", "Max_Humidity", "Time_Max_Humidity", "Min_Humidity", "Time_Min_Humidity", "Evapotranspiration"]

        df.columns = col_names
        # convert to DateTime object
        df['Date'] = pd.to_datetime(df['Date'], format='%Y%m%d')

        # filter out data before 2021
        df = df.loc[(df['Date'] >= KNMI_START_DATE)]

        # filter out columns the most relevant to our research
        df = df.drop(columns=["Sun_Duration", "Pct_Max_Sun", "Radiation", "Precip_Duration", "Precip_Amt",
                              "Max_Precip", "Time_Max_Precip", "Min_Visibility", "Time_Min_Visibility",
                              "Max_Visibility",
                              "Time_Max_Visibility", "Avg_Cloud_Cover", "Evapotranspiration"])


        return df
