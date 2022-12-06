from sklearn.decomposition import PCA


class DailyPatternsAnalyzer(object):
    def __init__(
        self, df, resample_to="H", start_time="6:30", end_time="17:00"
    ):
        self._df = (
            df.resample(resample_to)
            .mean()
            .between_time(start_time, end_time)
            .reset_index()
        )

    def pca(self, components, n_dims=2):
        df = self._df[[*components, "timestamp", "sensor_name"]]
        df["day"] = df["timestamp"].dt.floor("D")
        df["hour"] = df.timestamp.dt.hour
        # X shape is (n_samples, n_features). the features should be the hours
        # of the day, times the number of components, times the number of
        # sensors
        X = None
        pca = PCA(n_components=n_dims)
        pca.fit(X)
