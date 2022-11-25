import matplotlib.pyplot as plt
import pandas as pd
import geopandas as gpd

from mcs.constants import ASSETS_DIR, ROOT_DIR

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
    """ Plots a simple line for 1 column of 1 or more DataFrames

    Keyword arguments:
    dflist -- ((List of) DataFrame)
    col -- Column name (string)
    yscale -- y-axis scale (string)
    xlabel -- (string)
    ylabel -- (string)
    title -- (string)
    legend -- ((list of) string)
    outliers -- quantiles to remove (tuple)
    outfile -- name of output file (string)
"""
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
