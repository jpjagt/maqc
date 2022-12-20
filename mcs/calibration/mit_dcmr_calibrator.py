import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import statsmodels.api as sm
import pylab
import scipy.stats as stats

from mcs import plot
from mcs.models import (
    get_linear_regression_model,
    get_polynomial_regression_model,
    get_random_forest_model,
)
from mcs.estimators import RegressionEstimator
from mcs.log_encoder import LogEncoder


def set_inf_and_zero_vals_to_nan(df, col):
    df.loc[
        ((df[col] == np.inf) | (df[col] == 0.0)),
        col,
    ] = np.nan


def filter_dict_by_keys(dic, keys):
    return {key: value for key, value in dic.items() if key in keys}


def plot_predicted_vs_target_vals(
    estimator,
    source_x_col,
    y_col,
    component,
    ylim=None,
    display_predicted=True,
    title=None,
    plot_kwargs={},
    secondary_y_label=None,
):
    # plt.figure(figsize=(4 * 1.5, 3 * 1.5))
    plt.figure(figsize=(12, 8))
    ax = plt.gca()
    df = estimator._df_train.sort_index()
    df_decoded = estimator._encoder.decode_X(df)
    plot_df = pd.DataFrame(index=df.index)
    plot_df["Actual (DCMR)"] = estimator._encoder.decode_y(df[y_col])
    if display_predicted:
        plot_df["Predicted"] = estimator.predict(df_decoded)
    plot_df["Raw (MIT)"] = df_decoded[source_x_col]
    # plot_df = plot_df.rolling(window=80).mean().asfreq("10s")
    plot_df.plot(ax=ax, alpha=0.8, **plot_kwargs)
    component_pretty = plot.AxPrettifier.label2pretty_label.get(
        component, component
    )
    if title is None:
        plt.title(f"Predicted vs target {component_pretty}.")
    else:
        plt.title(title)
    ax.set_ylabel(component)
    ax.set_xlabel("Calibration period")

    if plot_kwargs.get("secondary_y") and secondary_y_label:
        ax.right_ax.set_ylabel(secondary_y_label)

    if ylim:
        ax.set_ylim(ylim)
    plot.PlotSaver("calibration").savefig(
        f"{component}/predicted_vs_target_vals"
    )
    plt.clf()


class MITDCMRCalibrator(object):
    # initialize calibration class
    def __init__(
        self,
        plot_results=False,
        component2model_choices={
            "pm25": [
                "linear_regression",
                "polynomial_regression",
                # "random_forest",
            ],
            "no2": [
                "linear_regression",
                "polynomial_regression",
                # "random_forest",
            ],
        },
    ):
        self._plot_results = plot_results
        self._component2model_choices = component2model_choices
        self._has_trained = False

    def _get_trained_model(
        self,
        df,
        x_cols,
        y_col,
        name2model__estimator_options,
        general_estimator_options={},
        source_x_col=None,
    ):
        results_df = None
        best_estimator = None
        best_estimator_name = None
        best_r2 = None

        if self._plot_results:
            # plot scatter
            if source_x_col is not None:
                df.plot.scatter(x=source_x_col, y=y_col)
                plt.xlabel(source_x_col)
                plt.ylabel(y_col)
                # plt.show()
        for name, (model, extra_opts) in name2model__estimator_options.items():
            estimator = RegressionEstimator(
                model=model,
                df=df,
                x_cols=x_cols,
                y_col=y_col,
                **general_estimator_options,
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
            if source_x_col is not None:
                results_df[source_x_col] = best_estimator._df_test[
                    source_x_col
                ]
                if best_estimator._encoder and (
                    source_x_col
                    in getattr(
                        best_estimator._encoder,
                        "_x_cols_to_encode",
                        [],
                    )
                ):
                    results_df[
                        source_x_col
                    ] = best_estimator._encoder.decode_y(
                        results_df[source_x_col]
                    )

            # Plot estimated values aganist target variable for RF and PM25
            results_df.plot(alpha=0.5)
            plt.gca().set_ylim(
                (
                    results_df.quantile(0.02).min() * 0.9,
                    results_df.quantile(0.98).max() * 1.1,
                )
            )
            plt.legend()
            plt.title(
                f"performance of various models. best model: {best_estimator_name}"
            )

            y_pred = results_df[f"{best_estimator_name} y_pred"]
            y_test = results_df["y_test"]

            # Generate residuals plot for Polynomial model(PM25)
            # and RF for NO2
            residuals = y_test - y_pred
            data = pd.DataFrame(best_estimator._df_test.copy())
            data["residuals"] = residuals
            sns.pairplot(data=data, y_vars=["residuals"], x_vars=x_cols)

            # Generate qq of residuals plot for model PLR (PM25) and RF (NO2)
            plt.figure()
            sm.qqplot(residuals, line="45", fit=True, dist=stats.norm)
            plt.show()
            # pylab.show()

        return best_estimator

    def _get_trained_pm25_model(self, df):
        # define columns
        x_cols = [
            "mit_pm25",
            "mit_humidity",
            # "knmi_wind_speed_hourly",
            # "knmi_wind_max_gust",
            "knmi_temperature",
            # "knmi_sunshine_duration",
            # "knmi_global_radiation",
            # "knmi_precipitation_duration",
            # "knmi_precipitation_hourly",
            "knmi_air_pressure",
            "knmi_relative_humidity",
            # "knmi_is_foggy",
            # "knmi_is_raining",
            # "knmi_is_snowing",
            # "knmi_is_thundering",
            # "knmi_ice_formation",
        ]

        # target variable
        y_col = "dcmr_PM25"
        log_encoder = LogEncoder(x_cols_to_encode=["mit_pm25"])
        best_estimator = self._get_trained_model(
            df,
            x_cols=x_cols,
            source_x_col=x_cols[0],
            y_col=y_col,
            general_estimator_options={
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
                self._component2model_choices["pm25"],
            ),
        )
        return best_estimator

    def _train_calibrated_no2_model(self, hourly_df):
        # define columns
        x_cols = [
            "mit_no2_mv",
            # "mit_humidity",
            # "knmi_wind_speed_hourly",
            # "knmi_wind_max_gust",
            # "knmi_temperature",
            # "knmi_sunshine_duration",
            # "knmi_global_radiation",
            # "knmi_precipitation_duration",
            # "knmi_precipitation_hourly",
            # "knmi_air_pressure",
            # "knmi_relative_humidity",
            # "knmi_is_foggy",
            # "knmi_is_raining",
            # "knmi_is_snowing",
            # "knmi_is_thundering",
            # "knmi_ice_formation",
        ]

        # target variable
        y_col = "dcmr_no2"
        # we take the log of the target variable, but no x cols because we can
        # just take the raw mv
        log_encoder = LogEncoder(x_cols_to_encode=[])
        self._calibrated_no2_estimator = self._get_trained_model(
            hourly_df,
            x_cols=x_cols,
            source_x_col=x_cols[0],
            y_col=y_col,
            general_estimator_options={
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
                self._component2model_choices["no2"],
            ),
        )

        plot_predicted_vs_target_vals(
            self._calibrated_no2_estimator,
            "mit_no2_mv",
            "dcmr_no2",
            "no2",
            # ylim=(3.4, 65),
            display_predicted=False,
            plot_kwargs={"secondary_y": "Raw (MIT)"},
            title="Raw vs actual NO2",
            secondary_y_label="Raw NO2 signal (mV)",
        )

    def _train_calibrated_pm25_model_10sec(self, tensec_df):
        self._calibrated_pm25_estimator_10sec = self._get_trained_pm25_model(
            tensec_df
        )
        plot_predicted_vs_target_vals(
            self._calibrated_pm25_estimator_10sec,
            "mit_pm25",
            "dcmr_PM25",
            "pm25",
            ylim=(3.4, 65),
        )

    def _train_calibrated_pm25_model_hourly(self, hourly_df):
        self._calibrated_pm25_estimator_hourly = self._get_trained_pm25_model(
            hourly_df
        )

    def train(
        self, train_10sec_df, train_hourly_df, dcmr_10sec_df, dcmr_hourly_df
    ):
        # merge mit and knmi data with dcmr data
        tensec_df = train_10sec_df.merge(
            dcmr_10sec_df.add_prefix("dcmr_"),
            how="inner",
            left_index=True,
            right_index=True,
        )
        hourly_df = train_hourly_df.merge(
            dcmr_hourly_df.add_prefix("dcmr_"),
            how="inner",
            left_index=True,
            right_index=True,
        )
        self._train_calibrated_pm25_model_10sec(tensec_df)
        self._train_calibrated_pm25_model_hourly(hourly_df)
        self._train_calibrated_no2_model(hourly_df)
        self._has_trained = True

    def calibrate(self, experiment_10sec_df, experiment_hourly_df):
        if not self._has_trained:
            raise RuntimeError("you need to call .train() first")

        # 10sec
        experiment_10sec_df[
            "pm25_calibrated"
        ] = self._calibrated_pm25_estimator_10sec.predict(experiment_10sec_df)
        set_inf_and_zero_vals_to_nan(experiment_10sec_df, "pm25_calibrated")

        models = self._calibrated_pm25_estimator_10sec._results["estimator"]
        df_encoded = self._calibrated_pm25_estimator_10sec._encoder.encode_X(
            experiment_10sec_df
        )
        X = df_encoded[self._calibrated_pm25_estimator_10sec._x_cols].values
        X = self._calibrated_pm25_estimator_10sec._scaler.transform(X)
        # for i, model in enumerate(models):
        #     experiment_10sec_df[f"pm25_pred_{i}"] = model.predict(X)
        # experiment_10sec_df[
        #     [
        #         "pm25_pred_0",
        #         "pm25_pred_1",
        #         "pm25_pred_2",
        #         "pm25_pred_3",
        #         "pm25_pred_4",
        #     ]
        # ].plot(alpha=0.8)
        # plt.show()

        # hourly
        experiment_hourly_df[
            "pm25_calibrated"
        ] = self._calibrated_pm25_estimator_hourly.predict(
            experiment_hourly_df
        )
        set_inf_and_zero_vals_to_nan(experiment_hourly_df, "pm25_calibrated")

        experiment_hourly_df[
            "no2_calibrated"
        ] = self._calibrated_no2_estimator.predict(experiment_hourly_df)
        set_inf_and_zero_vals_to_nan(experiment_hourly_df, "no2_calibrated")

        return experiment_10sec_df, experiment_hourly_df
