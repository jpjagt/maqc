import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.model_selection import GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.linear_model import ElasticNet
from mcs.data_loaders import MITDataLoader


## loading the city scanner data, for sensors ams1, ams2, ams3, and ams4
mit_data_loader = MITDataLoader()
# this is the range that we want to load
MEASUREMENT_RANGE = slice("2022-11-29", "2022-12-6")
# the experiment name
MIT_EXPERIMENT_NAME = "final-city-scanner-data"
# these are the ids of the city scanners
MIT_CS_IDS = ["ams3", "ams4"]
# loading the data
mit_cs_id2df = {
    mit_cs_id: mit_data_loader.load_data(MIT_EXPERIMENT_NAME, mit_cs_id).loc[
        MEASUREMENT_RANGE, :
    ]
    for mit_cs_id in MIT_CS_IDS
}

mit_df_ams3 = mit_cs_id2df['ams3']
mit_df_ams4 = mit_cs_id2df['ams4']

combined = mit_df_ams3.merge(mit_df_ams4, how='outer', left_index=True, right_index=True)

mit_df = pd.concat(mit_cs_id2df)

