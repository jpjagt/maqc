def get_station_codes_from_columns(columns):
    return [
        col
        for col in columns
        if isinstance(col, str) and len(col) == 7 and col.startswith("NL")
    ]


def get_ts_df(df, ts_col="Begindatumtijd", resample_to=None):
    station_codes = get_station_codes_from_columns(df.columns)

    # set the ts col as the index, and get just the station measurements
    ts_df = df.set_index(ts_col)[station_codes]

    # make sure the data is chronological
    ts_df = ts_df.sort_index()

    # remove duplicate timestamps
    ts_df = ts_df[~ts_df.index.duplicated()]

    # make sure we have a row for every hour
    ts_df = ts_df.asfreq("H")

    # fill missing values using ffill
    ts_df[station_codes] = ts_df[station_codes].ffill()

    if resample_to:
        ts_df = ts_df.resample(resample_to).mean()

    return ts_df
