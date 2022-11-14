import matplotlib.pyplot as plt
import pandas as pd
import geopandas as gpd

from mcs.constants import ASSETS_DIR

amsterdam_geojson = gpd.read_file(
    str(ASSETS_DIR / "amsterdam_neighbourhoods.geojson")
)


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


def plot_line(df, variable, yscale="linear", xlabel=None, ylabel=None):
    if type(df) == pd.DataFrame:
        df = [df]

    fig, ax = plt.subplots()

    for item in df:
        ax.plot(item.index, item[variable])

    ax.set_yscale(yscale)

    if xlabel:
        ax.set_xlabel(xlabel)
    if ylabel:
        ax.set_ylabel(ylabel)


def plot_timestamps_of_mit_sensor(df, name=None):
    start = df.timestamp.min() + pd.DateOffset(minutes=-5)
    end = df.timestamp.max() + pd.DateOffset(minutes=5)

    df_times = pd.DataFrame(
        index=pd.date_range(start, end, freq="S"), columns=["sensor"]
    )
    df_times["sensor"] = False
    df_times.loc[df.timestamp, "sensor"] = True

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
