class InputDataPreprocessor(object):
    def __init__(
        self,
        mit_df,
        knmi_df,
        start_datetime,
        end_datetime,
    ):
        # Add prefix to identify knmi from CS data
        self._mit_df = (
            mit_df.add_prefix("mit_")
            .unstack(level=0)
            .loc[start_datetime:end_datetime]
        )

        self._knmi_df = knmi_df.add_prefix("knmi_")
        self._start_datetime = start_datetime
        self._end_datetime = end_datetime

    def _preprocess_pm25(self, mit_df):
        mit_df["mit_pm25_mean"] = mit_df["mit_PM25"].mean(axis=1)
        mit_df["mit_humidity_mean"] = mit_df["mit_humidity"].mean(axis=1)
        mit_df = mit_df[["mit_pm25_mean", "mit_humidity_mean"]]
        mit_df.columns = ["mit_pm25_mean", "mit_humidity_mean"]

        # drop rows with nan values
        mit_df = mit_df.dropna(how="any")
        # filter out extreme quantiles of pm25
        mit_df = mit_df[
            (mit_df["mit_pm25_mean"] > mit_df["mit_pm25_mean"].quantile(0.05))
            & (
                mit_df["mit_pm25_mean"]
                < mit_df["mit_pm25_mean"].quantile(0.95)
            )
        ]
        # filter out high rel humidity
        mit_df = mit_df[(mit_df["mit_humidity_mean"] < 90)]

        mit_df = mit_df.rename(
            columns={
                "mit_humidity_mean": "mit_humidity",
                "mit_pm25_mean": "mit_pm25",
            }
        )
        return mit_df[["mit_pm25", "mit_humidity"]]

    def get_10sec_data(self):
        mit_10sec_df = (
            self._mit_df[["mit_PM25", "mit_humidity"]].resample("10s").mean()
        )
        mit_10sec_df = self._preprocess_pm25(mit_10sec_df)

        knmi_10sec_df = self._knmi_df.asfreq("10s").ffill()
        df = mit_10sec_df.merge(
            knmi_10sec_df, how="left", left_index=True, right_index=True
        )
        if df.isna().any().any():
            raise ValueError(
                "there are nans in the merged df, which probably "
                "is due to the left merge (i.e. knmi_10sec_df "
                "doesn't cover same period as mit_10sec_df)."
            )
        return df

    def get_hourly_data(self):
        # take one hour mean from city scanner for NO2 and humidity to match
        # DCMR
        mit_hourly_df = (
            self._mit_df[["mit_PM25", "mit_gas_op2_w", "mit_humidity"]]
            .resample("1h")
            .mean()
        )

        # Create new dataframe with hourly values
        mit_hourly_df["mit_no2_mv_mean"] = mit_hourly_df["mit_gas_op2_w"].mean(
            axis=1
        )
        mit_hourly_df["mit_humidity_mean"] = mit_hourly_df[
            "mit_humidity"
        ].mean(axis=1)
        mit_hourly_df["mit_pm25"] = self._preprocess_pm25(mit_hourly_df)[
            "mit_pm25"
        ]
        mit_hourly_df = mit_hourly_df[
            ["mit_pm25", "mit_no2_mv_mean", "mit_humidity_mean"]
        ]
        mit_hourly_df.columns = ["mit_pm25", "mit_no2_mv", "mit_humidity"]

        # drop rows without measurements
        mit_hourly_df = mit_hourly_df.dropna(how="any")

        # join of hourly city scanner dataframe with knmi data
        knmi_hourly_df = self._knmi_df.asfreq("1h").ffill()
        df = mit_hourly_df.merge(
            knmi_hourly_df, how="left", left_index=True, right_index=True
        )

        if df.isna().any().any():
            raise ValueError(
                "there are nans in the merged df, which probably "
                "is due to the left merge (i.e. knmi_hourly_df "
                "doesn't cover same period as mit_hourly_df)."
            )

        return df
