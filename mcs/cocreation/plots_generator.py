"""
    - we show the humidity and temperature to give a bit of context

    - we show the humidity vs PM correlation scatters to talk about correlation
      between those two things

    - we show our PM daily patterns to show there's no clear daily pattern
      resulting from construction activity (tentative)

    - we show detected spikes in PM during construction, and perhaps we can
      link that to certain activity (but i haven't labeled the video footage
      yet)

    - we show the UFP levels

    - we show the snifferbike things

    - NOx and CO plotting
"""

import calendar
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt, dates as mdates
from datetime import time, datetime

from mcs.constants import FIGURES_DIR, DATE_FOR_RELATIVE_TIME_OF_DAY
from mcs.cocreation.mit_data_loader import CocreationMITDataLoader
from mcs.data_loaders import KNMIDataLoader, UFPDataLoader
from mcs import plot, utils

# this is the range that we want to load
DEFAULT_MEASUREMENT_RANGE = slice("2022-11-07", "2022-11-28")
# the experiment name
DEFAULT_MIT_EXPERIMENT_NAME = "ensemble-site-2022-full"
DEFAULT_UFP_EXPERIMENT_NAME = "ensemble-site-2022-full"
# these are the ids of the city scanners
DEFAULT_MIT_CS_IDS = ["ams1", "ams2", "ams3", "ams4"]
# the output dir of the plots
DEFAULT_OUTPUT_DIR = FIGURES_DIR / "cocreation"

DISPLAY_PLOTS_INSTEAD_OF_SAVING = False


class CocreationPlotsGenerator(object):
    def __init__(
        self,
        measurement_range=DEFAULT_MEASUREMENT_RANGE,
        mit_cs_ids=DEFAULT_MIT_CS_IDS,
        mit_experiment_name=DEFAULT_MIT_EXPERIMENT_NAME,
        max_rh_threshold=None,
        output_dir=DEFAULT_OUTPUT_DIR,
    ):
        self._max_rh_threshold = max_rh_threshold
        self._mit_cs_ids = mit_cs_ids
        self._mit_data_loader = CocreationMITDataLoader(
            measurement_range=measurement_range,
            experiment_name=mit_experiment_name,
            cs_ids=mit_cs_ids,
            max_rh_threshold=max_rh_threshold,
        )
        self._knmi_data_loader = KNMIDataLoader()
        self._ufp_data_loader = UFPDataLoader()
        self._output_dir = output_dir

    def _load_data(self):
        self.mit_df, self.mit_df_day = self._mit_data_loader.load_data()
        self.knmi_df = self._knmi_data_loader.load_data()

        ufp_device_name2df = {
            f"ufp-{device_name}": self._ufp_data_loader.load_data(
                DEFAULT_UFP_EXPERIMENT_NAME, device_name
            )
            for device_name in ["sensor1", "sensor2"]
        }
        self.ufp_df = pd.concat(
            ufp_device_name2df, names=["sensor_name", "timestamp"]
        )

    def _get_full_title(self, title):
        if self._max_rh_threshold:
            title += f" (with RH < {self._max_rh_threshold})"

        return title

    def _savefig(self, name):
        if DISPLAY_PLOTS_INSTEAD_OF_SAVING:
            return
        else:
            if self._max_rh_threshold:
                name += f"_maxrh{self._max_rh_threshold}"
            fpath = self._output_dir / f"{name}.png"
            fpath.parent.mkdir(exist_ok=True, parents=True)
            plt.savefig(str(fpath))

    def _plot_daily(self, component, freq="20min", data=None, **kwargs):
        if data is None:
            data = self.mit_df_day.reset_index()
        ax = plot.tsplot(
            data,
            component,
            **{"hue": "sensor_name", "freq": freq, **kwargs},
        )
        if data is None:
            ax.set_title(
                self._get_full_title(f"average daily {component} per {freq}")
            )

    def _plot_multiple_daily(self, cols, **kwargs):
        fig, axs = plt.subplots(len(cols), 1, figsize=(8, 4 * len(cols)))

        for ax, col in zip(axs, cols):
            self._plot_daily(col, ax=ax, **kwargs)

    def _plot_vertical_dailies(self):
        self._plot_multiple_daily(
            ["PM1", "humidity_corrected", "temperature"],
            hue_whitelist=["ams1", "ams2"],
        )
        self._savefig("daily_pm1_humidity_temperature_for_ams1_ams2")
        self._plot_multiple_daily(
            ["PM1", "PM25", "humidity_corrected"],
            hue_whitelist=["ams1", "ams2"],
        )
        self._savefig("daily_pm1_pm25_humidity_for_ams1_ams2")

        # plots split per weekday and weekend
        self._plot_multiple_daily(
            ["PM1", "PM25", "humidity_corrected"], hue="is_weekday"
        )
        self._savefig("daily_pm1_pm25_humidity_week_vs_weekend")
        self._plot_multiple_daily(
            ["PM1", "PM25", "humidity_corrected"], hue="day_of_week"
        )
        self._savefig("daily_pm1_pm25_humidity_for_days_of_week")

    def _plot_daily_no_agg(
        self,
        component,
        freq="1min",
        sensor_name_whitelist=["ams1", "ams2"],
        data=None,
        **kwargs,
    ):
        if data is None:
            data = self.mit_df_day.reset_index()

        df = (
            data.groupby(
                ["sensor_name", pd.Grouper(key="timestamp", freq=freq)]
            )[[component]]
            .mean()
            .reset_index()
        )
        if sensor_name_whitelist:
            df = df[df.sensor_name.isin(sensor_name_whitelist)]
        utils.set_timestamp_related_cols(df)
        plt.figure(figsize=(16, 9))
        ax = sns.lineplot(
            data=df,
            **{
                "x": "time_of_day",
                "y": "PM1",
                "hue": "date",
                "style": "sensor_name",
                **kwargs,
            },
        )
        plot.set_xaxis_format_to_time_of_day(ax)

        if data is None:
            plt.title(
                self._get_full_title(f"daily {component} patterns per {freq}")
            )

    def _plot_humidity(self):
        plt.figure(figsize=(16, 9))
        mit_df = (
            self.mit_df["humidity_corrected"]
            .unstack(level=0)
            .resample("H")
            .mean()
        )
        knmi_df = self.knmi_df[["relative_humidity"]]
        knmi_df.columns = ["knmi"]
        humidity_df = mit_df.merge(knmi_df, left_index=True, right_index=True)
        ax = plt.gca()
        humidity_df.plot(ylabel="relative humidity (%)", ax=ax)
        ax.set_ylim((0, 100))
        plt.title(
            self._get_full_title(
                "average hourly relative humidity of KNMI and of MIT sensors"
            )
        )
        self._savefig("relative_humidity_knmi_vs_sensors")

    def _plot_ufp_with_pm1(self, freq="20s"):
        ufp_df = self.ufp_df.unstack(level=0)[["LDSA"]].resample(freq).mean()
        mit_df = (
            self.mit_df.unstack(level=0)[["PM1", "PM25"]].resample(freq).mean()
        )

        df = (
            ufp_df.merge(mit_df, left_index=True, right_index=True, how="left")
            .rolling(window=15)
            .mean()
        )
        df.columns.names = ["component", "sensor_name"]
        df = df.melt(ignore_index=False)

        for date, component2ylim in [
            (
                "2022-11-24",
                {
                    "LDSA": (0, 100),
                    "PM1": (0, 20),
                    "PM25": (0, 70),
                },
            ),
            (
                "2022-11-25",
                {
                    "LDSA": (0, 100),
                    "PM1": (0, 20),
                    "PM25": (0, 70),
                },
            ),
        ]:
            g = sns.FacetGrid(
                df.loc[date].reset_index(),
                row="component",
                sharey=False,
                hue="sensor_name",
                # xlim=(pd.to_datetime(f"{date} 05:00"), pd.to_datetime(f"{date} 18:00"))
                aspect=1.4,
                height=5,
            )
            g.map_dataframe(sns.lineplot, x="timestamp", y="value")
            g.add_legend()
            plt.suptitle(
                f"average UFP LDSA (naneos), PM1 and PM2.5 (MIT) per {freq} on {date}"
            )
            for component, ax in g.axes_dict.items():
                ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
                ax.set_ylim(component2ylim[component])
            plt.subplots_adjust(top=0.85)
            self._savefig(f"ufp_vs_pm_per_{freq}_{date}")

    def _plot_component_per_wind_status(self, component, data=None):
        if data is None:
            data = self.mit_df_day

        df = data.unstack(level=0)[component]
        df["wind_direction"] = (
            df.index.to_series().round("H").map(self.knmi_df.wind_direction)
        )
        df["wind_speed"] = (
            df.index.to_series().round("H").map(self.knmi_df.wind_speed_hourly)
        )
        rel_df = (
            df.groupby(["wind_direction", "wind_speed"]).mean().reset_index()
        )

        fig, axs = plt.subplots(2, 2)

        for ax, sensor_name in zip(axs.ravel(), self._mit_cs_ids):
            sns.heatmap(
                ax=ax,
                data=rel_df.pivot(
                    index="wind_direction",
                    columns="wind_speed",
                    values=sensor_name,
                ),
            )
            ax.set_title(sensor_name)
        plt.suptitle(
            self._get_full_title(
                f"average {component} per sensor across hourly wind direction & speed (KNMI) during working hours"
            )
        )

    def _plot_component_full(
        self,
        component,
        component_unit,
        ylim,
        gb_rh=False,
        display_raining=False,
        full_ylim=None,
    ):
        plt.figure(figsize=(16, 9))
        ax = plt.gca()

        ams1_df = self.mit_df.loc["ams1"]

        ams1_timestamp2component = (
            ams1_df[component].asfreq("5s").resample("60s").mean()
        )
        ams1_low_rh_timestamp2component = (
            ams1_df.loc[ams1_df.humidity_corrected < 85, component]
            .asfreq("5s")
            .resample("60s")
            .mean()
        )

        main_alpha = 0.3 if gb_rh else 1.0
        ams1_timestamp2component.plot(
            alpha=main_alpha, label="all values", ax=ax
        )
        if gb_rh:
            ams1_low_rh_timestamp2component.plot(label="RH < 85", ax=ax)

        plot.add_vfills_working_hours(ax, ams1_df.date)
        if full_ylim:
            ax.set_ylim(full_ylim)
        ax.set_ylabel(component_unit)

        plt.legend()
        plt.title(f"{component} from ams1 during entire experiment")
        self._savefig(f"full_{component}/ams1_entire_experiment")

        for date in ams1_df.date.unique():
            plt.figure(figsize=(16, 9))
            ax = plt.gca()

            date_str = date.strftime("%Y-%m-%d")

            ams1_timestamp2component.loc[date_str].plot(
                alpha=main_alpha, label="all values", ax=ax
            )
            if gb_rh:
                try:
                    ams1_low_rh_timestamp2component.loc[date_str].plot(
                        label="RH < 85", ax=ax
                    )
                except KeyError:
                    ax.plot([0], [0], label="RH < 85")

            plot.add_vfills_working_hours(ax, pd.Series([date]))
            ax.set_ylim(ylim)
            ax.set_ylabel(component_unit)
            ax.set_xlim(
                (
                    datetime.combine(date, time(hour=2, minute=0)),
                    datetime.combine(date, time(hour=22, minute=0)),
                )
            )
            for i, hour_end in enumerate(
                (
                    self.knmi_df[date_str]
                    .loc[self.knmi_df[date_str].is_raining.astype(bool)]
                    .index
                )
            ):
                label = "raining" if i == 0 else None
                ax.axvspan(
                    hour_end - pd.DateOffset(minutes=59),
                    hour_end,
                    alpha=0.05,
                    color="blue",
                    label=label,
                )
            plt.legend()
            weekday = list(calendar.day_name)[date.weekday()]
            plt.title(f"{component} from ams1 on {weekday}, {date_str}")
            self._savefig(f"full_{component}/ams1_{date_str}")

    def _print_working_hours_table(self):
        ams1_df = self.mit_df.loc["ams1"]
        ams1_df_day = self.mit_df_day.loc["ams1"]
        ams1_df["is_working_hour"] = False
        ams1_df.loc[ams1_df_day.index, "is_working_hour"] = True
        print(
            ams1_df.reset_index()
            .groupby(["is_working_hour"])[["PM1", "co_mgm3", "no2_mgm3"]]
            .agg(["mean", "var"])
            .to_markdown()
        )

    def generate_plots(self):
        DEFAULT_OUTPUT_DIR.mkdir(exist_ok=True, parents=True)
        utils.rm_dir_contents(DEFAULT_OUTPUT_DIR)

        self._load_data()
        self._plot_humidity()
        self._plot_vertical_dailies()

        self._plot_daily("PM1", hue="is_weekday")
        self._savefig("pm1_week_vs_weekend")
        # self._plot_daily_no_agg(
        #     "PM1",
        #     data=self.mit_df_day[self.mit_df_day.is_weekday].reset_index(),
        #     sensor_name_whitelist=["ams1"],
        #     freq="1min",
        # )

        self._plot_daily_no_agg("PM1")
        self._savefig("pm1_no_aggregation")

        self._plot_daily_no_agg(
            "PM1",
            data=self.mit_df.reset_index(),
            sensor_name_whitelist=["ams1"],
            freq="1min",
            hue="is_weekday",
            units="date",
            estimator=None,
        )
        self._savefig("pm1_no_aggregation_for_ams1_weekday_vs_weekend")

        self._plot_ufp_with_pm1()
        self._plot_component_per_wind_status("PM1")
        self._plot_component_full(
            "PM1", "µg / m3", ylim=(0, 30), gb_rh=True, display_raining=True
        )
        self._plot_component_full(
            "no2_mgm3",
            "µg / m3",
            ylim=(0.33 * 2, 1.5 * 2),
            full_ylim=(0.33 * 2, 1.5 * 2),
        )
        self._plot_component_full(
            "co_mgm3",
            "µg / m3",
            ylim=(0.33 * 1.2, 1.5 * 1.2),
            full_ylim=(0.33 * 1.2, 1.5 * 1.2),
        )
        self._print_working_hours_table()

        self._plot_daily(
            "no2_mgm3",
            hue_whitelist=["ams1", "ams2"],
            data=self.mit_df.reset_index(),
        )
        ax = plt.gca()
        plot.add_vfills_working_hours(
            ax, [datetime.date(datetime(2000, 1, 1))]
        )

        ax.set_xlim(
            [
                pd.to_datetime(f"{DATE_FOR_RELATIVE_TIME_OF_DAY} 02:00"),
                pd.to_datetime(f"{DATE_FOR_RELATIVE_TIME_OF_DAY} 22:00"),
            ]
        )
        self._savefig("no2_daily")
