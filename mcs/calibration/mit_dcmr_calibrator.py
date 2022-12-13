import numpy as np
import matplotlib.pyplot as plt

from mcs.models import (
    get_linear_regression_model,
    get_polynomial_regression_model,
    get_random_forest_model,
)
from mcs.estimators import RegressionEstimator
from mcs.log_encoder import LogEncoder


def filter_dict_by_keys(dic, keys):
    return {key: value for key, value in dic.items() if key in keys}


class MITDCMRCalibrator(object):
    def __init__(
        self,
        plot_results=False,
        calibration_pm25_model_choices=["polynomial_regression"],
    ):
        self._plot_results = plot_results
        self._calibration_pm25_model_choices = calibration_pm25_model_choices
        self._has_trained = False

    def _train_calibrated_pm25_model(self, train_10sec_df, dcmr_10sec_df):
        df = train_10sec_df.merge(
            dcmr_10sec_df,
            how="inner",
            left_index=True,
            right_index=True,
        )
        x_cols = [
            "mit_pm25",
            "mit_humidity",
            # "knmi_wind_speed_hourly",
            # "knmi_wind_max_gust",
            "knmi_temperature",
            "knmi_sunshine_duration",
            "knmi_global_radiation",
            "knmi_precipitation_duration",
            # "knmi_precipitation_hourly",
            "knmi_air_pressure",
            "knmi_relative_humidity",
            # "knmi_is_foggy",
            # "knmi_is_raining",
            # "knmi_is_snowing",
            # "knmi_is_thundering",
            # "knmi_ice_formation",
        ]
        y_col = "dcmr_PM25"
        log_encoder = LogEncoder(x_cols_to_encode=["mit_pm25"])
        self._calibrated_pm25_estimator = self._get_trained_model(
            df,
            estimator_options={
                "x_cols": x_cols,
                "y_col": y_col,
                "encoder": log_encoder,
            },
            name2model__estimator_options=filter_dict_by_keys(
                {
                    "linear_regression": (
                        get_linear_regression_model(),
                        {},
                    ),
                    "polynomial_regression": (
                        get_polynomial_regression_model(degree=2),
                        {},
                    ),
                    "random_forest": (
                        get_random_forest_model(),
                        {"do_cross_validation": False},
                    ),
                },
                self._calibration_pm25_model_choices,
            ),
        )

    def _get_trained_model(
        self, df, estimator_options, name2model__estimator_options
    ):
        results_df = None
        best_estimator = None
        best_estimator_name = None
        best_r2 = None
        for name, (model, extra_opts) in name2model__estimator_options.items():
            if name not in self._calibration_pm25_model_choices:
                continue
            estimator = RegressionEstimator(
                model=model,
                df=df,
                **estimator_options,
                **extra_opts,
            )
            estimator.train()
            print(f"validation performance for {name}")
            r2, rmse, estimator_results_df = estimator.test()
            print()
            pred_col_name = f"{name} y_pred"
            estimator_results_df = estimator_results_df.rename(
                columns={"y_pred": pred_col_name}
            )
            if results_df is None:
                results_df = estimator_results_df
            else:
                results_df[pred_col_name] = estimator_results_df[pred_col_name]
            if best_r2 is None or r2 > best_r2:
                best_r2 = r2
                best_estimator = estimator
                best_estimator_name = name
        if self._plot_results:
            results_df.plot(alpha=0.5)
            plt.legend()
            plt.title(
                f"performance of various models. best model: {best_estimator_name}"
            )

            plt.figure()

            y_pred = results_df[f"{best_estimator_name} y_pred"]
            y_test = results_df["y_test"]
            plt.show()
        return best_estimator

    def train(
        self, train_10sec_df, train_hourly_df, dcmr_10sec_df, dcmr_hourly_df
    ):
        dcmr_10sec_df = dcmr_10sec_df.add_prefix("dcmr_")
        dcmr_hourly_df = dcmr_hourly_df.add_prefix("dcmr_")
        self._train_calibrated_pm25_model(train_10sec_df, dcmr_10sec_df)
        self._train_calibrated_no2_model(train_hourly_df, dcmr_hourly_df)
        self._has_trained = True

    def calibrate(self, experiment_10sec_df, experiment_hourly_df):
        if not self._has_trained:
            raise RuntimeError("you need to call .train() first")

        # 10sec
        experiment_10sec_df[
            "pm25_calibrated"
        ] = self._calibrated_pm25_estimator.predict(experiment_10sec_df)
        experiment_10sec_df.loc[
            (
                (experiment_10sec_df["pm25_calibrated"] == np.inf)
                | (experiment_10sec_df["pm25_calibrated"] == 0.0)
            ),
            "pm25_calibrated",
        ] = np.nan

        # hourly
        experiment_hourly_df[
            "no2_calibrated"
        ] = self._calibrated_no2_estimator.predict(experiment_hourly_df)

        return experiment_10sec_df, experiment_hourly_df
