import pandas as pd
from functools import lru_cache

from mcs.constants import GGD_STATION_TYPES
from mcs.data_loaders import GGDDataLoader


def compute_weighted_mean_background_level(
    ggd_df,
    ggd_station_metadata_df,
    station_type2weight={"achtergrond": 1.0, "industrie": 0.0, "verkeer": 0.3},
):
    """
    given background level measurements from multiple GGD stations in ggd_df,
    and the ggd station metadata, compute a weighted mean background level.

    :param station_type2weight: optionally, pass a dictionary to give different
        weights to different station types in the mean (if a station_type is
        missing, it will be given a default weight of 1.0).
    """
    # set default weights
    for station_type in GGD_STATION_TYPES:
        if station_type not in station_type2weight:
            station_type2weight[station_type] = 1.0

    # get the weight per station code
    station_code2weight = ggd_station_metadata_df.loc[
        ggd_df.columns, "Stationstype"
    ].map(station_type2weight)
    # ensure that we are taking the mean by ensuring weights sum to 1
    station_code2weight = station_code2weight / station_code2weight.sum()

    # compute the weighted mean
    weighted_mean = ggd_df[station_code2weight.keys()].dot(station_code2weight)
    return weighted_mean


@lru_cache
def load_ggd_data(component):
    ggd_data_loader = GGDDataLoader()
    ggd_df = ggd_data_loader.load_all(component)
    ggd_station_metadata_df = ggd_data_loader.load_all_station_metadata()
    return ggd_df, ggd_station_metadata_df


def subtract_background_level_with_ggd_data(
    series_or_df, component, station_type2weight={}
):
    """
    subtract the background levels of the given component from a series or df which
    maps timestamps to the levels.

    :param station_type2weight: optionally, pass a dictionary to give different
        weights to different station types in the mean (if a station_type is
        missing, it will be given a default weight of 1.0).
    """
    # load the ggd data
    ggd_df, ggd_station_metadata_df = load_ggd_data(component)

    # only take the period present in series. we include one hour of padding
    # just to make sure we won't be missing any data later on
    date_range = slice(
        (series_or_df.index.min().floor("h") - pd.DateOffset(hours=1)),
        (series_or_df.index.max().ceil("h") + pd.DateOffset(hours=1)),
    )
    ggd_df = ggd_df.loc[date_range]

    weighted_mean = compute_weighted_mean_background_level(
        ggd_df,
        ggd_station_metadata_df,
        station_type2weight=station_type2weight,
    )
    # make sure we have a matching weighted mean timestamp for each row in the
    # series
    rel_weighted_mean = weighted_mean.resample("s").ffill()[series_or_df.index]

    def _subtract(series):
        return series - rel_weighted_mean

    if isinstance(series_or_df, pd.Series):
        result = _subtract(series_or_df)
    else:
        result = series_or_df.apply(_subtract, axis=0)
    return result, rel_weighted_mean


def set_cols_without_bg(df, col2component):
    for col, component in col2component.items():
        if col in df:

            def _set_cols(target_name, result):
                # always set on full index, also if result is a series, because
                # of consistency with later operations
                target_name = pd.MultiIndex.from_product(
                    [[target_name], df[col].columns]
                )
                if isinstance(result, pd.Series):
                    for target_col in target_name:
                        df[target_col] = result
                else:
                    df[target_name] = result

            (
                result,
                rel_weighted_mean,
            ) = subtract_background_level_with_ggd_data(df[col], component)
            _set_cols(f"{col}_nobg", result)
            _set_cols(f"{col}_bg", rel_weighted_mean)
    return df
