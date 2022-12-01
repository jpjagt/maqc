import pandas as pd

from mcs.data_loaders import MITDataLoader
from mcs.constants import (
    START_TIME,
    END_TIME,
)

RELEVANT_COLUMNS = [
    "deviceID",
    "latitude",
    "longitude",
    "PM1",
    "PM25",
    # "PM10",
    "temperature",
    "humidity_corrected",
    "gas_op1_w",
    "gas_op1_r",
    "gas_op2_w",
    "gas_op2_r",
    "src_fpath",
    "time_of_day",
    "day_of_week",
    "date",
]

ROLLING_WINDOW_SIZE = 30


class CocreationMITDataLoader(object):
    def __init__(
        self,
        measurement_range,
        experiment_name,
        cs_ids,
        start_time=START_TIME,
        end_time=END_TIME,
    ):
        self._measurement_range = measurement_range
        self._experiment_name = experiment_name
        self._cs_ids = cs_ids
        self._start_time = start_time
        self._end_time = end_time

    def _set_humidity_corrected(self, df):
        # humidity_opc has a more accurate pattern, as it's not clamped at
        # 100%. however, based on plots, it looks like the mean levels of
        # 'humidity' are better than 'humidity_opc'.
        df["humidity_corrected"] = df["humidity_opc"]
        df["humidity_corrected"] += (
            df["humidity"].mean() - df["humidity_corrected"].mean()
        )
        return df

    def _correct_pm(self, df):
        for component in ["PM1", "PM25"]:
            component_df = df[component]
            mi = pd.MultiIndex.from_product(
                [[f"{component}_corrected"], list(self._cs_ids)]
            )
            df[mi] = component_df.rolling(ROLLING_WINDOW_SIZE).mean()
        return df

    def load_data(self):
        # loading the city scanner data
        data_loader = MITDataLoader()

        # loading the data for each sensor
        mit_cs_id2df = {
            cs_id: data_loader.load_data(self._experiment_name, cs_id).loc[
                self._measurement_range, :
            ]
            for cs_id in self._cs_ids
        }
        # combine them into a single dataframe
        df = pd.concat(mit_cs_id2df, names=["sensor_name", "timestamp"])

        # correct the humidity
        df = self._set_humidity_corrected(df)

        # make sensor_name part of columns and not index
        df = df.unstack(level=0)

        # now we do time-series related transformations, so we can only do it
        # after unstacking

        # correct PM
        df = self._correct_pm(df)

        # only return the columns which are relevant
        df = df[RELEVANT_COLUMNS]

        # only take data between start and end time
        df = (
            df.between_time(self._start_time, self._end_time)
            .stack()
            .swaplevel()
        )

        return df
