from mcs.data_loaders import (
    CalibratedDataLoader,
    KNMIDataLoader,
    CameraImageLabelsDataLoader,
    UFPDataLoader,
    MITDataLoader,
    GGDDataLoader,
)

import numpy as np
import calendar
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt, dates as mdates
from datetime import time, datetime

from mcs.constants import (
    DATE_FOR_RELATIVE_TIME_OF_DAY,
    START_TIME,
    END_TIME,
    EXPERIMENT_START_DATE,
    EXPERIMENT_END_DATE,
    CALIBRATION_START_DATETIME,
    CALIBRATION_END_DATETIME,
)
from mcs import plot, utils

# the experiment name
DEFAULT_CALIBRATED_DATA_NAME = "final-results"
DEFAULT_UFP_EXPERIMENT_NAME = "ensemble-site-2022-full"
# these are the ids of the city scanners
DEFAULT_MIT_CS_IDS = ["ams1", "ams2", "ams3", "ams4"]


class PlotsGenerator(object):
    def __init__(
        self,
        name,
        mit_df,
        tensec_df,
        hourly_df,
        knmi_df,
        ufp_df,
        camera_image_labels_df=None,
        max_rh_threshold=None,
        mit_cs_ids=DEFAULT_MIT_CS_IDS,
    ):
        self._max_rh_threshold = max_rh_threshold
        self._mit_cs_ids = mit_cs_ids
        self._mit_df = mit_df
        self._tensec_df = tensec_df
        self._hourly_df = hourly_df
        self._knmi_df = knmi_df
        self._ufp_df = ufp_df
        self._camera_image_labels_df = camera_image_labels_df

        if self._max_rh_threshold:
            suffix = f"_maxrh{self._max_rh_threshold}"
        else:
            suffix = None
        self._plot_saver = plot.PlotSaver(name, suffix)

    def _get_full_title(self, title):
        if self._max_rh_threshold:
            title += f" (with RH < {self._max_rh_threshold})"

        return title

    def _plot_daily(
        self,
        component,
        data=None,
        freq="20min",
        **kwargs,
    ):
        if data is None:
            data = self._tensec_df.reset_index()
            utils.set_timestamp_related_cols(data)

        if kwargs.get("hue") == "is_weekday":
            if "is_weekday" not in data:
                utils.set_timestamp_related_cols(data)
            if set(data.is_weekday.unique()) == {True, False}:
                data.is_weekday = data.is_weekday.map(
                    {False: "Weekend", True: "Week"}
                )
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
        fig, axs = plt.subplots(len(cols), 1, figsize=(10, 5 * len(cols)))

        for ax, col in zip(axs, cols):
            self._plot_daily(col, ax=ax, **kwargs)

    def _plot_vertical_dailies(self):
        self._plot_multiple_daily(
            ["pm25_calibrated_nobg", "mit_humidity"],
            hue_whitelist=["ams1", "ams2"],
        )
        self._plot_saver.savefig("daily_pm25_and_humidity_for_ams1_ams2")

        # plots split per weekday and weekend
        self._plot_multiple_daily(
            ["pm25_calibrated_nobg", "mit_humidity"], hue="is_weekday"
        )
        self._plot_saver.savefig("daily_pm1_pm25_humidity_week_vs_weekend")

        self._plot_multiple_daily(
            ["pm25_calibrated_nobg", "mit_humidity"], hue="day_of_week"
        )
        self._plot_saver.savefig("daily_pm1_pm25_humidity_for_days_of_week")

    def _plot_daily_no_agg(
        self,
        component,
        freq="1min",
        sensor_name_whitelist=["ams1", "ams2"],
        data=None,
        **kwargs,
    ):
        if data is None:
            data = self._tensec_df.reset_index()

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
        plt.figure(figsize=(11, 7))
        ax = sns.lineplot(
            data=df,
            **{
                "x": "time_of_day",
                "y": "pm25_calibrated_nobg",
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

    def _plot_pm25_calibrated_nobg_vs_uncalibrated(self):
        df = (
            self._tensec_df.loc["ams1", ["mit_pm25", "pm25_calibrated_nobg"]]
            .rename(
                columns={
                    "mit_pm25": "Uncalibrated",
                    "pm25_calibrated_nobg": "Calibrated",
                }
            )
            .melt(var_name="ams1", value_name="pm25", ignore_index=False)
        ).reset_index()
        utils.set_timestamp_related_cols(df)
        self._plot_daily("pm25", hue="ams1", data=df)
        self._plot_saver.savefig("pm25_uncalibrated_vs_calibrated")

    def _plot_ufp_with_pm25(
        self,
        freq="20s",
        limit_xaxis_by_component="LDSA",
    ):
        ufp_df = self._ufp_df.unstack(level=0)[["LDSA"]].resample(freq).mean()
        tensec_df = (
            self._tensec_df.unstack(level=0)[["pm25_calibrated_nobg"]]
            .resample(freq)
            .mean()
        )

        df = (
            ufp_df.merge(
                tensec_df, left_index=True, right_index=True, how="left"
            )
            .rolling(window=10)
            .mean()
        )
        df.columns.names = ["component", "sensor_name"]
        df = df.asfreq(freq).melt(ignore_index=False)
        # drop all rows without value
        df = df.dropna(subset=["value"])

        for date, component2ylim in [
            (
                "2022-11-24",
                {
                    "LDSA": (0, 100),
                    "pm25_calibrated_nobg": (0, 70),
                },
            ),
            (
                "2022-11-25",
                {
                    "LDSA": (0, 100),
                    "pm25_calibrated_nobg": (0, 70),
                },
            ),
        ]:
            row = "component"
            x = "timestamp"
            data_on_date = df.loc[date].reset_index()
            xlim_bounds = data_on_date.loc[
                data_on_date.component == limit_xaxis_by_component, x
            ].agg(["min", "max"])
            xlim = tuple(
                (
                    xlim_bounds[["min", "max"]]
                    + pd.Series(
                        {
                            "min": pd.DateOffset(hours=-1),
                            "max": pd.DateOffset(hours=1),
                        }
                    )
                ).values
            )

            g = sns.FacetGrid(
                data_on_date,
                row=row,
                sharey=False,
                hue="sensor_name",
                xlim=xlim,
                aspect=1.4,
                height=5,
            )
            g.map_dataframe(sns.lineplot, x="timestamp", y="value")
            g.add_legend()
            plt.suptitle(
                f"mean UFP LDSA (naneos) and PM2.5 (MIT) per {freq} on {date}"
            )
            for component, ax in g.axes_dict.items():
                ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
                ax.set_ylim(component2ylim[component])
            plt.subplots_adjust(top=0.85)
            self._plot_saver.savefig(f"ufp_vs_pm_per_{freq}_{date}")

    def _plot_component_full(
        self,
        component,
        component_unit,
        ylim,
        gb_rh=False,
        display_raining=False,
        full_ylim=None,
    ):
        plt.figure(figsize=(11, 7))
        ax = plt.gca()

        ams1_df = self._tensec_df.loc["ams1"]

        ams1_timestamp2component = (
            ams1_df[component].asfreq("5s").resample("60s").mean()
        )
        ams1_low_rh_timestamp2component = (
            ams1_df.loc[ams1_df.mit_humidity < 85, component]
            .asfreq("5s")
            .resample("60s")
            .mean()
        )

        main_alpha = 0.3 if gb_rh else 1.0
        ams1_timestamp2component.plot(
            alpha=main_alpha, label="all values", ax=ax
        )
        if gb_rh:
            ams1_low_rh_timestamp2component.plot(
                label="relative humidity < 85", ax=ax
            )

        utils.set_timestamp_related_cols(ams1_df)
        plot.add_vfills_working_hours(ax, ams1_df.date)
        if full_ylim:
            ax.set_ylim(full_ylim)
        ax.set_ylabel(component)
        ax.set_xlabel("Date")
        component_pretty = plot.AxPrettifier.label2pretty_label.get(
            component, component
        )
        plt.legend()
        plt.title(f"{component_pretty} for AMS1 over entire experiment")
        self._plot_saver.savefig(f"full_{component}/ams1_entire_experiment")

        utils.set_timestamp_related_cols(ams1_df)

        for date in ams1_df.date.unique():
            plt.figure(figsize=(11, 7))
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
                    self._knmi_df[date_str]
                    .loc[self._knmi_df[date_str].is_raining.astype(bool)]
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
            self._plot_saver.savefig(f"full_{component}/ams1_{date_str}")

    def _print_working_hours_table(self):
        for df, col in [
            (self._tensec_df, "pm25_calibrated"),
            (self._tensec_df, "pm25_calibrated_nobg"),
            (self._hourly_df, "no2_calibrated"),
        ]:
            ams1_df = df.loc["ams1"]
            ams1_df_day = ams1_df.between_time(START_TIME, END_TIME)
            ams1_df["is_working_hour"] = False
            ams1_df.loc[ams1_df_day.index, "is_working_hour"] = True
            print(
                ams1_df.reset_index()
                .groupby(["is_working_hour"])[[col]]
                .agg(["mean", "var"])
                .to_markdown()
            )

    def _plot_sensor_coverage(self):
        plot.sensor_active_plot(
            self._mit_df,
            vspan_period2name={
                (
                    EXPERIMENT_START_DATE,
                    EXPERIMENT_END_DATE,
                ): "Experiment period",
                (
                    CALIBRATION_START_DATETIME,
                    CALIBRATION_END_DATETIME,
                ): "Calibration period",
            },
        )
        plt.gca().set_xlim(
            (
                pd.to_datetime(EXPERIMENT_START_DATE).floor("d"),
                pd.to_datetime(CALIBRATION_END_DATETIME).ceil("d"),
            )
        )
        plt.title(
            "Measurement coverage per sensor during experiment + calibration"
        )
        self._plot_saver.savefig("sensor_coverage")

    def _generate_infographic_plots(self):
        # Uncalibrated data vs. Calibrated
        plt.figure(figsize=(4 * 1.8, 3 * 1.8))
        ax = plt.gca()
        df = (
            self._tensec_df.loc["ams1", ["mit_pm25", "pm25_calibrated"]]
            .rename(
                columns={
                    "mit_pm25": "Uncalibrated (ams1)",
                    "pm25_calibrated": "Calibrated (ams1)",
                }
            )
            .melt(var_name="variable", value_name="pm25", ignore_index=False)
        ).reset_index()
        utils.set_timestamp_related_cols(df)
        self._plot_daily("pm25", hue="variable", data=df, ax=ax)
        ax.set_ylim((0, 45))
        self._plot_saver.savefig("infographic/pm25_uncalibrated_vs_calibrated")

        # Background pollution subtracted, ams1, weekday
        plt.figure(figsize=(4 * 1.8, 3 * 1.8))
        ax = plt.gca()

        df = self._tensec_df.loc["ams1"].reset_index()
        utils.set_timestamp_related_cols(df)
        df["is_weekday"] = df["is_weekday"].map(
            {False: "Weekend (ams1)", True: "During week (ams1)"}
        )
        self._plot_daily(
            "pm25_calibrated_nobg", hue="is_weekday", data=df, ax=ax
        )
        ax.set_ylim((0, 45))
        self._plot_saver.savefig(
            "infographic/pm25_bg_subtracted_ams1_week_vs_weekend"
        )

        # Background pollution subtracted, hue=sensor
        plt.figure(figsize=(4 * 1.8, 3 * 1.8))
        ax = plt.gca()

        df = self._tensec_df.loc[["ams1", "ams3", "ams4"]].reset_index()
        utils.set_timestamp_related_cols(df)
        self._plot_daily("pm25_calibrated_nobg", ax=ax, data=df)
        self._plot_saver.savefig("infographic/pm25_bg_subtracted_per_sensor")

    def generate_plots(self):
        self._plot_saver.rm_existing_plots()
        self._generate_infographic_plots()

        self._plot_daily(
            "pm25_calibrated_nobg",
            hue="is_weekday",
            data=self._tensec_df.loc["ams1"],
        )
        self._plot_saver.savefig(
            "daily_pm25_calibrated_nobg_for_ams1_week_vs_weekend"
        )

        self._plot_vertical_dailies()

        self._plot_daily("pm25_calibrated_nobg", hue="is_weekday")
        self._plot_saver.savefig("pm25_week_vs_weekend")

        self._plot_pm25_calibrated_nobg_vs_uncalibrated()

        self._plot_daily_no_agg("pm25_calibrated_nobg")
        self._plot_saver.savefig("pm25_no_aggregation")

        self._plot_daily_no_agg(
            "pm25_calibrated_nobg",
            data=self._tensec_df.reset_index(),
            sensor_name_whitelist=["ams1"],
            freq="1min",
            hue="is_weekday",
            units="date",
            estimator=None,
        )
        self._plot_saver.savefig(
            "pm25_no_aggregation_for_ams1_weekday_vs_weekend"
        )

        data = (
            self._mit_df.reset_index(level=0).copy().resample("60min").mean()
        )
        # ggd_no2 = GGDDataLoader().load_all("NO2")['NL49021']
        # pd.DataFrame({"gas_op2_w": ggd_no2, 'GGD (NL49021)'
        # data[("gas_op2_w", )] =
        # self._plot_daily(
        #     "gas_op2_w",
        #     data=data.reset_index(),
        #     freq="60min",
        #     # secondary_y=("gas_op2_w", "GGD (NL49021)"),
        # )
        # self._plot_saver.savefig("daily_raw_no2_signals_during_experiment")

        raw_no2_per_2min = (
            self._mit_df.reset_index(level=0)
            .resample("2min")
            .gas_op2_w.mean()
            .asfreq("2min")
        )
        camera_image_labels_df = self._camera_image_labels_df.copy().set_index(
            "timestamp"
        )
        camera_image_labels_df["gas_op2_w"] = raw_no2_per_2min
        plt.figure(figsize=(11, 7))
        ax = (
            camera_image_labels_df.reset_index()
            .pivot(
                index="timestamp",
                columns="nof_active_vehicles",
                values="gas_op2_w",
            )
            .drop(columns=[np.nan])
            .rename(columns=int)
            .plot.box()
        )
        ax.set_ylim((250, 530))
        plt.title("Distribution of mean raw NO2 per # of active vehicles")
        ax.set_ylabel("gas_op2_w")
        ax.set_xlabel("nof_active_vehicles")
        self._plot_saver.savefig("raw_no2_per_nof_active_vehicles")

        self._plot_ufp_with_pm25()
        self._plot_component_full(
            "pm25_calibrated_nobg",
            "µg / m3",
            ylim=(0, 30),
            gb_rh=True,
            display_raining=True,
        )
        # self._plot_component_full(
        #     "no2_calibrated_nobg",
        #     "PPM",
        #     ylim=(0.33 * 2, 1.8 * 2),
        #     full_ylim=(0.33 * 2, 1.8 * 2),
        # )
        self._print_working_hours_table()


def generate_final_plots(
    name,
    mit_experiment_name,
    mit_cs_ids,
    calibrated_results_name,
    knmi_station_code,
    ufp_experiment_name,
    ufp_sensors,
):
    mit_df = MITDataLoader().load_data(mit_experiment_name, mit_cs_ids)
    calibrated_data_loader = CalibratedDataLoader(calibrated_results_name)
    print("loading calibrated data...")
    tensec_df = calibrated_data_loader.load_data("10sec")
    hourly_df = calibrated_data_loader.load_data("hourly")
    print("loading knmi data...")
    knmi_df = KNMIDataLoader().load_data(knmi_station_code)
    print("loading ufp data...")
    ufp_df = UFPDataLoader().load_data(ufp_experiment_name, ufp_sensors)
    camera_image_labels_df = CameraImageLabelsDataLoader().load_data(
        "img_labels_15-28nov"
    )

    print("initializing PlotsGenerator...")
    PlotsGenerator(
        name=name,
        mit_df=mit_df,
        tensec_df=tensec_df,
        hourly_df=hourly_df,
        knmi_df=knmi_df,
        ufp_df=ufp_df,
        camera_image_labels_df=camera_image_labels_df,
        max_rh_threshold=None,
        mit_cs_ids=mit_cs_ids,
    ).generate_plots()


if __name__ == "__main__":
    generate_final_plots(
        name="livinglab",
        mit_experiment_name="final-city-scanner-data",
        mit_cs_ids=["ams1", "ams2", "ams3", "ams4"],
        calibrated_results_name="final-data",
        knmi_station_code="240",
        ufp_experiment_name="ensemble-site-2022-full",
        ufp_sensors=["sensor1", "sensor2"],
    )
