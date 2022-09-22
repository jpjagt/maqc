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
