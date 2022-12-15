import pandas as pd
import fire

from mcs.data_loaders import (
    MITDataLoader,
    KNMIDataLoader,
    DCMRDataLoader,
    CalibratedDataLoader,
)
from mcs.constants import (
    CALIBRATION_START_DATETIME,
    CALIBRATION_END_DATETIME,
    EXPERIMENT_START_DATE,
    EXPERIMENT_END_DATE,
)
from mcs.calibration.input_data_preprocessor import InputDataPreprocessor
from mcs.calibration.mit_dcmr_calibrator import MITDCMRCalibrator


def write_calibrated_data(
    mit_experiment_name="final-city-scanner-data",
    dcmr_experiment_name="schiedam-december-2022",
    output_name="final-data",
    calibration_sensor_names=["ams3", "ams4"],
    experiment_sensor_names=["ams1", "ams2", "ams3", "ams4"],
    calibration_start_datetime=CALIBRATION_START_DATETIME,
    calibration_end_datetime=CALIBRATION_END_DATETIME,
    experiment_start_datetime=EXPERIMENT_START_DATE,
    experiment_end_datetime=EXPERIMENT_END_DATE,
    calibration_knmi_station_code="344",
    experiment_knmi_station_code="240",
    plot_calibration_training_results=True,
):
    calibration_mit_df = MITDataLoader().load_data(
        mit_experiment_name, calibration_sensor_names
    )
    calibration_knmi_df = KNMIDataLoader().load_data(
        calibration_knmi_station_code,
        start_date=calibration_start_datetime,
        end_date=calibration_end_datetime,
    )
    dcmr_10sec_df = DCMRDataLoader().load_10sec_data(
        dcmr_experiment_name,
    )
    dcmr_hourly_df = DCMRDataLoader().load_hourly_data(
        dcmr_experiment_name,
    )

    calibration_data_preprocessor = InputDataPreprocessor(
        calibration_mit_df,
        calibration_knmi_df,
        start_datetime=calibration_start_datetime,
        end_datetime=calibration_end_datetime,
    )

    calibration_10sec_df = calibration_data_preprocessor.get_10sec_data()
    calibration_hourly_df = calibration_data_preprocessor.get_hourly_data()

    calibrator = MITDCMRCalibrator(
        plot_results=plot_calibration_training_results
    )
    calibrator.train(
        dcmr_10sec_df=dcmr_10sec_df,
        dcmr_hourly_df=dcmr_hourly_df,
        train_10sec_df=calibration_10sec_df,
        train_hourly_df=calibration_hourly_df,
    )

    experiment_knmi_df = KNMIDataLoader().load_data(
        experiment_knmi_station_code,
        start_date=experiment_start_datetime,
        end_date=experiment_end_datetime,
    )
    sensor_name210sec_df = {}
    sensor_name2hourly_df = {}
    for sensor_name in experiment_sensor_names:
        experiment_mit_df = MITDataLoader().load_data(
            mit_experiment_name, [sensor_name]
        )
        experiment_data_preprocessor = InputDataPreprocessor(
            experiment_mit_df,
            experiment_knmi_df,
            start_datetime=experiment_start_datetime,
            end_datetime=experiment_end_datetime,
        )
        experiment_10sec_df = experiment_data_preprocessor.get_10sec_data()
        experiment_hourly_df = experiment_data_preprocessor.get_hourly_data()
        experiment_10sec_df, experiment_hourly_df = calibrator.calibrate(
            experiment_10sec_df, experiment_hourly_df
        )
        sensor_name210sec_df[sensor_name] = experiment_10sec_df
        sensor_name2hourly_df[sensor_name] = experiment_hourly_df

    cdl = CalibratedDataLoader(output_name)
    cdl.write_data("10sec", pd.concat(sensor_name210sec_df))
    cdl.write_data("hourly", pd.concat(sensor_name2hourly_df))


if __name__ == "__main__":
    fire.Fire(write_calibrated_data)
