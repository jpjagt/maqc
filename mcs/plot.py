import matplotlib
from matplotlib import pyplot as plt, dates as mdates
import itertools
import numpy as np
import pandas as pd
import seaborn as sns
import geopandas as gpd
from windrose import WindroseAxes

from mcs.constants import (
    FIGURES_DIR,
    ASSETS_DIR,
    ROOT_DIR,
    DATE_FOR_RELATIVE_TIME_OF_DAY,
    START_TIME,
    END_TIME,
)
from mcs.utils import rm_dir_contents, set_timestamp_related_cols

MPL_DPI = 300
matplotlib.rcParams["savefig.dpi"] = MPL_DPI

amsterdam_geojson = gpd.read_file(
    str(ASSETS_DIR / "amsterdam_neighbourhoods.geojson")
)

sns.set()


def plot_points_lat_lng(df, label_column=None):
    gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.lng, df.lat))

    ax = amsterdam_geojson.plot(color="white", edgecolor="black")
    gdf.plot(ax=ax, color="red")

    if label_column:
        for x, y, label in zip(
            gdf.geometry.x, gdf.geometry.y, gdf[label_column]
        ):
            ax.annotate(
                label, xy=(x, y), xytext=(3, 3), textcoords="offset points"
            )


def plot_line(
    dflist,
    col,
    yscale="linear",
    xlabel=None,
    ylabel=None,
    legend=None,
    title=None,
    outliers=None,
    outfile=None,
):
    """Plots a simple line for 1 column of 1 or more DataFrames

    Keyword arguments:
    dflist -- ((List of) DataFrame)
    col -- Column name (string)
    yscale -- y-axis scale (string)
    xlabel -- (string)
    ylabel -- (string)
    title -- (string)
    legend -- ((list of) string)
    outliers -- quantiles to remove (tuple)
    outfile -- name of output file (string)"""
    if type(dflist) == pd.DataFrame:
        dflist = [dflist]

    fig, ax = plt.subplots()

    for df in dflist:
        if outliers != None:
            q_low = df[col].quantile(outliers[0])
            q_hi = df[col].quantile(outliers[1])
            df = df[(df[col] < q_hi) & (df[col] > q_low)]
        ax.plot(df.index, df[col])

    ax.set_yscale(yscale)

    if xlabel:
        ax.set_xlabel(xlabel)
    if ylabel:
        ax.set_ylabel(ylabel)
    if legend:
        ax.legend(legend)
    if title:
        ax.set_title(title)

    if outfile != None:
        fig.savefig(str(ROOT_DIR / ("exports/" + outfile + ".svg")))
    fig.show()


def plot_timestamps_of_mit_sensor(df, name=None):
    start = df.index.min() + pd.DateOffset(minutes=-5)
    end = df.index.max() + pd.DateOffset(minutes=5)

    df_times = pd.DataFrame(
        index=pd.date_range(start, end, freq="S"), columns=["sensor"]
    )
    df_times["sensor"] = False
    df_times.loc[df.index, "sensor"] = True

    df_times.astype(int).plot(alpha=0.5)

    if name:
        plt.title(f"recorded timestamps for {name}")


def plot_col_of_multiple_sensors(name2series, colname):
    df = pd.DataFrame(name2series)
    start = df.index.min() + pd.DateOffset(minutes=-5)
    end = df.index.max() + pd.DateOffset(minutes=5)

    index = pd.date_range(start, end, freq="S")
    df = df.reindex(index)

    df.astype(float).plot(alpha=0.5)
    plt.ylabel(colname)


def plot_col_of_multiple_sensors2(dflist, colname):
    df = pd.DataFrame()
    for tmpdf in dflist:
        df = df.append(tmpdf)
    start = df.index.min() + pd.DateOffset(minutes=-5)
    end = df.index.max() + pd.DateOffset(minutes=5)

    index = pd.date_range(start, end, freq="S")
    df = df.reindex(index)

    df.astype(float).plot(alpha=0.5)
    plt.ylabel(colname)


def set_xaxis_format_to_time_of_day(
    ax, set_xlim=True, use_working_hour_boundaries=False
):
    if use_working_hour_boundaries:
        start_time = START_TIME
        end_time = END_TIME
    else:
        start_time = "00:00"
        end_time = "23:59"
    if set_xlim:
        ax.set_xlim(
            [
                pd.to_datetime(f"{DATE_FOR_RELATIVE_TIME_OF_DAY} {start_time}")
                + pd.DateOffset(minutes=-15),
                pd.to_datetime(f"{DATE_FOR_RELATIVE_TIME_OF_DAY} {end_time}")
                + pd.DateOffset(minutes=15),
            ]
        )
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))


palette = list(sns.color_palette())


def tsplot(
    data, y, ax=None, hue=None, hue_whitelist=None, freq=None, set_xlim=True
):
    x = "time_of_day"

    if x not in data and "timestamp" in data:
        data = data.copy()
        set_timestamp_related_cols(data)

    if ax is None:
        plt.figure(figsize=(11, 7))
        ax = plt.gca()

    if hue is None:
        hue_vals = [None]
    else:
        hue_vals = data[hue].unique()

    for color, val in zip(palette, hue_vals):
        if hue_whitelist is not None:
            if val not in hue_whitelist:
                continue

        if val is None:
            rel_df = data
        else:
            rel_df = data[data[hue] == val]

        gb = x if freq is None else pd.Grouper(freq=freq, key=x)

        agg_df = (
            rel_df.groupby(gb)[y]
            .agg(["mean", "std"])
            .sort_index()
            .reset_index()
        )

        xdata = agg_df[x]
        est = agg_df["mean"]
        sd = agg_df["std"]
        cis = (est - sd, est + sd)
        ax.fill_between(
            xdata, cis[0], cis[1], alpha=0.1, color=color, label=val
        )
        ax.plot(xdata, est, color=color)

    ax.set_xlabel(x)
    ax.set_ylabel(y)
    ax.margins(x=0)

    if x == "time_of_day":
        set_xaxis_format_to_time_of_day(ax, set_xlim=set_xlim)
        add_vfills_working_hours(
            ax, [DATE_FOR_RELATIVE_TIME_OF_DAY], only_weekday=False
        )

    plt.legend()

    return ax


def windrose(data, wind_direction_col, y_col):
    fig, ax = plt.subplots(figsize=(11, 11), dpi=80)
    ax = WindroseAxes.from_ax()
    ax.bar(
        data[wind_direction_col],
        data[y_col],
        normed=True,
        opening=0.8,
        edgecolor="white",
    )
    ax.set_legend()


def add_vfills_working_hours(ax, dates, only_weekday=True):
    date_unique = pd.to_datetime(pd.Series(np.unique(dates)))

    if only_weekday:
        # only select week days
        date_unique = date_unique[date_unique.dt.dayofweek <= 4]

    def _get_dates_with_timeoffset(time_str):
        hours, mins = map(int, time_str.split(":"))
        return date_unique + pd.DateOffset(hours=hours, minutes=mins)

    first_loop = True
    for start_moment, end_moment in zip(
        _get_dates_with_timeoffset(START_TIME),
        _get_dates_with_timeoffset(END_TIME),
    ):
        if first_loop:
            label = "Working hours"
            first_loop = False
        else:
            label = None
        ax.axvspan(
            start_moment,
            end_moment,
            alpha=0.12,
            color="black",
            label=label,
        )


def sensor_active_plot(mit_df, vspan_period2name={}):
    plt.figure(figsize=(12, 6))
    df = mit_df.index.to_frame().reset_index(drop=True)
    df["is_present"] = True
    sensor_names = list(reversed(sorted(df.sensor_name.unique())))
    df = (
        df.pivot(index="timestamp", columns="sensor_name", values="is_present")
        .asfreq("10s")
        .fillna(False)
    )

    ax = plt.gca()

    for i, sensor_name in enumerate(sensor_names):
        y = i + 1
        ax.fill_between(
            df.index,
            y - 0.25,
            y + 0.25,
            where=df[sensor_name],
            interpolate=False,
            color=palette[i],
        )
    ax.set_yticks(range(1, len(sensor_names) + 1), labels=sensor_names)

    # rotate the xticks by 30 degrees
    plt.xticks(rotation=30)

    for i, (vspan_period, name) in enumerate(vspan_period2name.items()):
        color = palette[i + len(sensor_names)]
        ax.axvspan(
            pd.to_datetime(vspan_period[0]),
            pd.to_datetime(vspan_period[1]),
            alpha=0.17,
            color=color,
            label=name,
        )
        plt.legend()


class AxPrettifier(object):
    label2pretty_label = {
        "time_of_day": "Time of day",
        "pm25": "PM2.5",
        "gas_op2_w": "Raw NO2 signal",
        "mit_pm25": "Uncalibrated PM2.5",
        "mit_pm25_nobg": "Uncalibrated PM2.5 minus BG",
        "pm25_calibrated": "Calibrated PM2.5",
        "pm25_uncalibrated": "Uncalibrated PM2.5",
        "pm25_calibrated_nobg": "Calibrated PM2.5 minus BG",
        "pm25_uncalibrated_nobg": "Uncalibrated PM2.5 minus BG",
        "no2": "NO2",
        "humidity": "Relative humidity",
        "mit_humidity": "Relative humidity",
        "knmi_relative_humidity": "Relative humidity",
        "nof_active_vehicles": "# active vehicles",
    }

    label2unit = {
        "time_of_day": "HH:MM",
        "pm25": "µg/m³",
        "mit_pm25": "µg/m³",
        "gas_op2_w": "mV",
        "pm25_calibrated": "µg/m³",
        "pm25_uncalibrated": "µg/m³",
        "pm25_calibrated_nobg": "µg/m³",
        "pm25_uncalibrated_nobg": "µg/m³",
        "no2": "PPM",
        "no2_calibrated": "PPM",
        "no2_calibrated_nobg": "PPM",
        "humidity": "%",
        "mit_humidity": "%",
        "knmi_relative_humidity": "%",
    }

    def __init__(self, ax):
        self._ax = ax

    def _prettify_label(self, label, set_fn):
        if (pretty_label := self.label2pretty_label.get(label)) is not None:
            unit = self.label2unit.get(label)
            if unit is not None:
                pretty_label += f" ({unit})"
            set_fn(pretty_label)

    def prettify(self):
        self._prettify_label(self._ax.get_xlabel(), self._ax.set_xlabel)
        self._prettify_label(self._ax.get_ylabel(), self._ax.set_ylabel)


class PlotSaver(object):
    # extension = "svg"
    # extension = "png"
    extension = "jpg"

    def __init__(self, name, suffix=None, skip_save=False):
        self._name = name
        self._suffix = suffix
        self._dir = FIGURES_DIR / self._name
        self._skip_save = skip_save

    def make_current_plot_pretty(self):
        axs = plt.gcf().get_axes()
        if not isinstance(axs, np.ndarray):
            axs = np.array([axs])
        for ax in axs.ravel():
            AxPrettifier(ax).prettify()

    def savefig(self, name):
        self.make_current_plot_pretty()

        if self._skip_save:
            return
        else:
            if self._suffix:
                name += self._suffix
            fname = f"{name}.{self.extension}"
            fpath = self._dir / fname
            fpath.parent.mkdir(exist_ok=True, parents=True)
            print(f"[PlotSaver] saving {fname}")
            plt.tight_layout()
            plt.savefig(str(fpath), bbox_inches="tight", dpi=MPL_DPI)

    def rm_existing_plots(self):
        rm_dir_contents(self._dir)
