import matplotlib.pyplot as plt

from mcs.cocreation.mit_data_loader import CocreationMITDataLoader
from mcs.data_loaders import KNMIDataLoader, UFPDataLoader

DEFAULT_UFP_EXPERIMENT_NAME = "ensemble-site-2022-full"


class CocreationResultsPlotter(ResultsPlotter):
    def __init__(
        self,
        measurement_range=DEFAULT_MEASUREMENT_RANGE,
        mit_cs_ids=DEFAULT_MIT_CS_IDS,
        mit_experiment_name=DEFAULT_MIT_EXPERIMENT_NAME,
        max_rh_threshold=None,
        output_dir=DEFAULT_OUTPUT_DIR,
    ):

self._mit_data_loader = CocreationMITDataLoader(
            measurement_range=measurement_range,
            experiment_name=mit_experiment_name,
            cs_ids=mit_cs_ids,
            max_rh_threshold=max_rh_threshold,
        )
        self._knmi_data_loader = KNMIDataLoader()
        self._ufp_data_loader = UFPDataLoader()

    def _load_data(self):
        self.mit_df, self.mit_df = self._mit_data_loader.load_data()
        self.knmi_df = self._knmi_data_loader.load_data("240")
        self.ufp_df = self._ufp_data_loader.load_data(
            DEFAULT_UFP_EXPERIMENT_NAME, ["sensor1", "sensor2"]
        )
