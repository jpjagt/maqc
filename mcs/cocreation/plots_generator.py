import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt

from mcs.cocreation.mit_data_loader import CocreationMITDataLoader
from mcs.data_loaders import KNMIDataLoader
from mcs import plot, utils

# this is the range that we want to load
DEFAULT_MEASUREMENT_RANGE = slice("2022-11-07", "2022-11-28")
# the experiment name
DEFAULT_MIT_EXPERIMENT_NAME = "ensemble-site-2022-full"
# these are the ids of the city scanners
DEFAULT_MIT_CS_IDS = ["ams1", "ams2", "ams3", "ams4"]

FIGSIZE = (16, 9)


class CocreationPlotsGenerator(object):
    def __init__(
        self,
        measurement_range=DEFAULT_MEASUREMENT_RANGE,
        mit_cs_ids=DEFAULT_MIT_CS_IDS,
        mit_experiment_name=DEFAULT_MIT_EXPERIMENT_NAME,
    ):
        self._mit_data_loader = CocreationMITDataLoader(
            measurement_range=measurement_range,
            experiment_name=mit_experiment_name,
            cs_ids=mit_cs_ids,
        )
        self._knmi_data_loader = KNMIDataLoader()

    def _plot_daily(self, component, freq="20min", **kwargs):
        plot.tsplot(
            self.mit_df.reset_index(),
            component,
            hue="sensor_name",
            freq=freq,
            **kwargs
        )

    def _plot_multiple_daily(self, cols):
        fig, axs = plt.subplots(len(cols), 1)
        hue_whitelist = ["ams3", "ams4"]

        for ax, col in zip(axs, cols):
            self._plot_daily(col, ax=ax, hue_whitelist=hue_whitelist)

    def _plot_vertical_dailies(self):
        self._plot_multiple_daily(["PM1", "humidity_corrected", "temperature"])
        self._plot_multiple_daily(["PM1", "PM25", "humidity_corrected"])

    def _plot_daily_no_agg(
        self,
        component,
        freq="1min",
        sensor_name_whitelist=["ams1", "ams2"],
        **kwargs
    ):
        df = (
            self.mit_df.reset_index()
            .groupby(["sensor_name", pd.Grouper(key="timestamp", freq=freq)])[
                [component]
            ]
            .mean()
            .reset_index()
        )
        if sensor_name_whitelist:
            df = df[df.sensor_name.isin(sensor_name_whitelist)]
        utils.set_timestamp_related_cols(df)
        sns.lineplot(
            data=df,
            x="time_of_day",
            y="PM1",
            hue="sensor_name",
            style="date",
            **kwargs
        )

    def _plot_humidity(self):
        plt.figure(figsize=FIGSIZE)
        mit_df = (
            self.mit_df["humidity_corrected"]
            .unstack(level=0)
            .resample("H")
            .mean()
        )
        knmi_df = self.knmi_df[["relative_humidity"]]
        knmi_df.columns = ["knmi"]
        humidity_df = mit_df.merge(knmi_df, left_index=True, right_index=True)
        humidity_df.plot(ylabel="relative humidity (%)")

    def _load_data(self):
        self.mit_df = self._mit_data_loader.load_data()
        self.knmi_df = self._knmi_data_loader.load_data()

    def generate_plots(self):
        self._load_data()
        self._plot_humidity()
        self._plot_vertical_dailies()
        self._plot_daily_no_agg("PM1")
