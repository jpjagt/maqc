from mcs.data_loaders import MITDataLoader, GVBDataLoader
import pandas as pd

COLORS = ["orange", "dodgerblue", "firebrick"]

sensor_df = MITDataLoader().load_data("kyra-balcony", "w4-nyc-02")
sensor_df = sensor_df.set_index('timestamp').sort_index().asfreq("5S")
start, end = sensor_df.index.min(), sensor_df.index.max()

gvb_departures_away = GVBDataLoader().load_departures_in_range(
    "hdvries-away-2022", start, end
)
gvb_departures_return = GVBDataLoader().load_departures_in_range(
    "hdvries-return-2022", start, end
)

gvb_departures = pd.concat(
    [pd.Series(gvb_departures_away), pd.Series(gvb_departures_return)]
)
gvb_departures = gvb_departures[(gvb_departures > start) & (gvb_departures < end)]

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np


def plot_components(
    components,
    window=40,
    sensor_df=sensor_df,
    gvb_departures_away=gvb_departures_away,
    gvb_departures_return=gvb_departures_return,
):
    if not isinstance(components, (list, tuple)):
        components = [components]

    all_vals = sensor_df[components].values[~sensor_df[components].isna().values]
    ymin, ymax = (
        np.percentile(all_vals, 1),
        np.percentile(all_vals, 99),
    )

    plt.close("all")
    plt.figure(figsize=(12, 9))
    plt.ylim(ymin, ymax)
    ax = plt.gca()
    ax.vlines(
        x=gvb_departures_away.values,
        ymin=ymin,
        ymax=ymax,
        colors="purple",
        alpha=0.5,
        label="departure time of tram (away)",
    )
    ax.vlines(
        x=gvb_departures_return.values,
        ymin=ymin,
        ymax=ymax,
        colors="green",
        alpha=0.5,
        label="departure time of tram (return)",
    )
    for i, component in enumerate(components):
        color = COLORS[i]
        ax.plot(
            sensor_df.index,
            sensor_df[component].values,
            alpha=0.2,
            c=color,
        )
        ax.plot(
            sensor_df.index,
            sensor_df[component].rolling(window=window).mean().values,
            c=color,
            label=f"{component} (rolling mean, window={window})",
        )
    plt.legend()
    plt.title(f"{', '.join(components)} and nearby tram stop departure times")

plot_components(["PM25", "PM10"])
plt.show()

o30_start = "2022-09-30 10:30"
o30_end = "2022-09-30 20:30"

sensor_df_o30 = sensor_df[o30_start:o30_end]
gvb_departures_away_o30 = gvb_departures_away[
    (gvb_departures_away > o30_start) & (gvb_departures_away < o30_end)
]
gvb_departures_return_o30 = gvb_departures_return[
    (gvb_departures_return > o30_start) & (gvb_departures_return < o30_end)
]


def plot_components_o30(components, *args, **kwargs):
    plot_components(
        components,
        *args,
        **kwargs,
        sensor_df=sensor_df_o30,
        gvb_departures_away=gvb_departures_away_o30,
        gvb_departures_return=gvb_departures_return_o30,
    )
    ax = plt.gca()
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))
    ax.xaxis.set_minor_formatter(mdates.DateFormatter("%H:%M:%S"))
    ax.set_xlabel("time of day (hh:mm:ss)")
    plt.title(
        f"{', '.join(components)} and nearby tram stop departure times on Oct 30th"
    )

plot_components_o30(["PM10", "PM25"])
ax = plt.gca()
ax.set_ylabel("concentration (µg/m³)")
plt.show()

from scipy.spatial import distance


def departures_to_coords(departures):
    return [(val, 0) for val in (departures.astype(np.int64) // 10 ** 9).values]


min_distances_seconds = distance.cdist(
    departures_to_coords(gvb_departures_away_o30),
    departures_to_coords(gvb_departures_return_o30),
).min(axis=1)

print("\ndifference between departure time value counts (seconds):")
print(pd.Series(min_distances_seconds.astype(int)).value_counts())
print("========================================")
print("mean (seconds):", min_distances.mean())
print("var (seconds):", min_distances.var())
print(
    "fraction of trams which depart within 3 minutes of each other:",
    ((min_distances < 180).mean().round(2) * 100),
    "%",
)

from string import Template


class DeltaTemplate(Template):
    delimiter = "%"


def strfdelta(tdelta, fmt):
    d = {"D": tdelta.days}
    hours, rem = divmod(tdelta.seconds, 3600)
    minutes, seconds = divmod(rem, 60)
    d["H"] = "{:02d}".format(hours)
    d["M"] = "{:02d}".format(minutes)
    d["S"] = "{:02d}".format(seconds)
    t = DeltaTemplate(fmt)
    return t.substitute(**d)


def get_average(
    departures, sensor_df, components, radius=pd.DateOffset(minutes=3)
):
    sensor_df_filled = sensor_df[components].ffill()
    departure_ranges = [
        slice(departure - radius, departure + radius)
        for departure in departures
    ]
    ary = np.array(
        [
            [
                sensor_df_filled.loc[departure_range, component].values
                for departure_range in departure_ranges
            ]
            for component in components
        ]
    )
    center = datetime.now()
    relative_daterange = pd.date_range(
        center - radius, center + radius, freq="5S"
    )[: ary.shape[2]]
    df = pd.DataFrame(
        index=relative_daterange,
        columns=pd.MultiIndex.from_product([components, ("mean", "std")]),
    )
    df.loc[:, (slice(None), "mean")] = ary.mean(axis=1).T
    df.loc[:, (slice(None), "std")] = ary.std(axis=1).T
    return df, center


def plot_avg(df, center, departure_name, date_name, departure_vline_color):
    plt.figure()
    ax = plt.gca()
    ymax = (
        (
            df.loc[:, (slice(None), "mean")].values
            + df.loc[:, (slice(None), "std")].values
        )
        .max()
        .max()
    )
    plt.ylim(0, ymax)
    for i, component in enumerate(set(df.columns.get_level_values(0))):
        color = COLORS[i]
        df.loc[:, (component, "mean")].plot(ax=ax, color=color, label=f"{component} (mean)")
        ax.fill_between(
            df.index,
            (df[(component, "mean")] - df[(component, "std")]),
            df[(component, "mean")] + df[(component, "std")],
            color=color,
            alpha=0.3,
            label=f"{component} (std)",
        )
    ax.vlines(
        [center],
        ymin=0,
        ymax=ymax,
        label="departure time",
        colors=departure_vline_color,
    )
    radius = center - df.index.min()
    one_third_radius = radius / 3
    radii_thirds = [
        strfdelta(td, "%M:%S")
        for td in [one_third_radius, one_third_radius * 2, radius]
    ]
    ax.set_xticks(
        [
            center - radius,
            center - one_third_radius * 2,
            center - one_third_radius,
            center,
            center + one_third_radius,
            center + one_third_radius * 2,
            center + radius,
        ],
        [f"-{rt}" for rt in radii_thirds[::-1]] + ["0"] + radii_thirds,
    )
    ax.set_ylabel("concentration (µg/m³)")
    ax.set_xlabel("time offset from departure time (mm:ss)")
    plt.legend()
    plt.title(
        f"average concentrations around '{departure_name}' departure times {date_name}"
    )


plot_avg(
    *get_average(gvb_departures_away_o30, sensor_df, ["PM25", "PM10"]),
    "away",
    "on Oct 30th",
    "purple",
)
plt.show()
plot_avg(
    *get_average(gvb_departures_return_o30, sensor_df, ["PM25", "PM10"]),
    "return",
    "on Oct 30th",
    "green",
)
plt.show()
