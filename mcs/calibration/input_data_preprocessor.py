class InputDataPreprocessor(object):
    def __init__(
        self,
        mit_df,
        knmi_df,
        start_datetime,
        end_datetime,
    ):
        self._mit_df = (
            mit_df.add_prefix("mit_")
            .unstack(level=0)
            .loc[start_datetime:end_datetime]
        )
        self._knmi_df = knmi_df.add_prefix("knmi_")
        self._start_datetime = start_datetime
        self._end_datetime = end_datetime

    def get_10sec_data(self):
        mit_10sec_df = (
            self._mit_df[["mit_PM25", "mit_humidity"]].resample("10s").mean()
        )
        mit_10sec_df["mit_pm25_mean"] = mit_10sec_df["mit_PM25"].mean(axis=1)
        mit_10sec_df["mit_humidity_mean"] = mit_10sec_df["mit_humidity"].mean(
            axis=1
        )
        mit_10sec_df = mit_10sec_df[["mit_pm25_mean", "mit_humidity_mean"]]
        mit_10sec_df.columns = ["mit_pm25_mean", "mit_humidity_mean"]
        mit_10sec_df = mit_10sec_df.dropna()
        # filter out extreme quantiles
        mit_10sec_df = mit_10sec_df[
            (
                mit_10sec_df["mit_pm25_mean"]
                > mit_10sec_df["mit_pm25_mean"].quantile(0.05)
            )
            & (
                mit_10sec_df["mit_pm25_mean"]
                < mit_10sec_df["mit_pm25_mean"].quantile(0.95)
            )
        ]
        # filter out high rel humidity
        mit_10sec_df = mit_10sec_df[(mit_10sec_df["mit_humidity_mean"] < 90)]

        knmi_10sec_df = self._knmi_df.asfreq("10s").ffill()
        df = mit_10sec_df.merge(
            knmi_10sec_df, how="left", left_index=True, right_index=True
        )
        return df

    def get_hourly_data(self):
        self._mit_hourly_df = (
            self._mit_df[["mit_gas_op2_w"]].resample("1h").mean()
        )
