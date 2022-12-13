import matplotlib.pyplot as plt
import sklearn 
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline
import pandas as pd
import seaborn as sns 

from mcs.constants import (
    CALIBRATION_START_DATETIME,
    CALIBRATION_END_DATETIME,
    EXPERIMENT_START_DATE,
    EXPERIMENT_END_DATE,
)
from mcs.estimators import RegressionEstimator
from mcs.calibration.input_data_preprocessor import InputDataPreprocessor
from mcs.log_encoder import LogEncoder


class MITDCMRCalibrator(object):
    #initialize calibration class
    def __init__(
        self,
        plot_results=False,
        calibration_pm25_model_choices=["polynomial_regression"],
    ):
        self._plot_results = plot_results
        self._calibration_pm25_model_choices = calibration_pm25_model_choices
        self._has_trained = False

    def _train_calibrated_pm25_model(self, train_10sec_df, dcmr_10sec_df):
        #merge mit and knmi data with dcmr data 
        df = train_10sec_df.merge(
            dcmr_10sec_df,
            how="inner",
            left_index=True,
            right_index=True,
        )
        #define columns 
        x_cols = [
            "mit_pm25_mean",
            "mit_humidity_mean",
            "knmi_wind_speed_hourly",
            "knmi_wind_max_gust",
            "knmi_temperature",
            "knmi_sunshine_duration",
            "knmi_global_radiation",
            "knmi_precipitation_duration",
            "knmi_precipitation_hourly",
            "knmi_air_pressure",
            "knmi_relative_humidity",
            "knmi_is_foggy",
            "knmi_is_raining",
            "knmi_is_snowing",
            "knmi_is_thundering",
            "knmi_ice_formation",
        ]
        # Numerical columns 
        x_cols_num = [
            "mit_pm25_mean",
            "mit_humidity_mean",
            "knmi_temperature",
            "knmi_relative_humidity",
            "knmi_air_pressure",
            ]

        #target variable 
        y_col = "dcmr_PM25"
        log_encoder = LogEncoder(x_cols_to_encode=["mit_pm25_mean"])

        results_df = None
        best_estimator = None
        best_estimator_name = None
        best_r2 = None
        for name, (model, opts) in {
            "linear_regression": (LinearRegression(), {}),
            "polynomial_regression": (
                make_pipeline(
                    PolynomialFeatures(degree=2, include_bias=False),
                    LinearRegression(),
                ),
                {},
            ),
            "random_forest": (
                RandomForestRegressor(
                    **{
                        "n_estimators": 200,
                        "max_features": "sqrt",
                        "min_samples_split": 4,
                        "min_samples_leaf": 0.01,
                    }
                ),
                {"do_cross_validation": False},
            ),
        }.items():
            if name not in self._calibration_pm25_model_choices:
                continue
            estimator = RegressionEstimator(
                model=model,
                df=df,
                x_cols=x_cols,
                y_col=y_col,
                encoder=log_encoder,
                **opts,
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

            #Plot estimated values aganist target variable 
            results_df.plot(alpha=0.5)
            plt.legend()
            plt.title(
                f"performance of various models. best model: {best_estimator_name}"
            )

            plt.figure()
            y_pred = results_df[f"{best_estimator_name} y_pred"]
            y_test = results_df["y_test"]
           
           # Generate residuals plot for Polynomial model 
            residuals = y_test - y_pred
            data = pd.DataFrame(best_estimator._df_test.copy())
            data['residuals'] = residuals
            sns.pairplot(data=data,
                  y_vars=['residuals'],
                  x_vars=x_cols_num)
            plt.show()

           
        self._calibrated_pm25_estimator = best_estimator

    def train(
        self, train_10sec_df, train_hourly_df, dcmr_10sec_df, dcmr_hourly_df
    ):
        dcmr_10sec_df = dcmr_10sec_df.add_prefix("dcmr_")
        dcmr_hourly_df = dcmr_hourly_df.add_prefix("dcmr_")
        self._train_calibrated_pm25_model(train_10sec_df, dcmr_10sec_df)
        self._has_trained = True

    def calibrate(self, experiment_10sec_df, experiment_hourly_df):
        if not self._has_trained:
            raise RuntimeError("you need to call .train() first")
        experiment_10sec_df[
            "pm25_calibrated"
        ] = self._calibrated_pm25_estimator.predict(experiment_10sec_df)


def calibrate():
    from mcs.data_loaders import MITDataLoader, KNMIDataLoader, DCMRDataLoader

    calibration_mit_df = MITDataLoader().load_data(
        "final-city-scanner-data", ["ams3", "ams4"]
    )
    calibration_knmi_df = KNMIDataLoader().load_data(
        "344",
        start_date=CALIBRATION_START_DATETIME,
        end_date=CALIBRATION_END_DATETIME,
    )
    dcmr_10sec_df = DCMRDataLoader().load_10sec_data(
        "schiedam-december-2022",
    )
    dcmr_hourly_df = DCMRDataLoader().load_hourly_data(
        "schiedam-december-2022",
    )

    calibration_data_preprocessor = InputDataPreprocessor(
        calibration_mit_df,
        calibration_knmi_df,
        start_datetime=CALIBRATION_START_DATETIME,
        end_datetime=CALIBRATION_END_DATETIME,
    )
    calibration_10sec_df = calibration_data_preprocessor.get_10sec_data()
    calibration_hourly_df = calibration_data_preprocessor.get_hourly_data()

    calibrator = MITDCMRCalibrator(plot_results=True)
    calibrator.train(
        dcmr_10sec_df=dcmr_10sec_df,
        dcmr_hourly_df=dcmr_hourly_df,
        train_10sec_df=calibration_10sec_df,
        train_hourly_df=calibration_hourly_df,
    )

    experiment_knmi_df = KNMIDataLoader().load_data(
        "240",
        start_date=EXPERIMENT_START_DATE,
        end_date=EXPERIMENT_END_DATE,
    )
    for sensor_name in ["ams1", "ams2"]:
        experiment_mit_df = MITDataLoader().load_data(
            "final-city-scanner-data", [sensor_name]
        )
        experiment_data_preprocessor = InputDataPreprocessor(
            experiment_mit_df,
            experiment_knmi_df,
            start_datetime=EXPERIMENT_START_DATE,
            end_datetime=EXPERIMENT_END_DATE,
        )
        experiment_10sec_df = experiment_data_preprocessor.get_10sec_data()
        experiment_hourly_df = experiment_data_preprocessor.get_hourly_data()
        calibrator.calibrate(experiment_10sec_df, experiment_hourly_df)
        experiment_10sec_df["pm25_calibrated"]
