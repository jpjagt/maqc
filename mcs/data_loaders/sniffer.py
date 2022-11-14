import pandas as pd

from mcs.constants import SNIFFER_DATA_DIR

class SNIFFERdataloader(object):
    def __init__(self):
        pass
    
    def _read_csv(self, fpath):
        df = pd.read_csv(
                fpath,
                sep=",",
                index_col=False,
            )
        return df

    def _pre_process(self, df):
        # filter out the relative humidity above 85%
        df = df[df["rh"] < 85]
        #Convert to datetime
        df["time"] =  pd.to_datetime(df["time"])
    

        return df

    def load_data(self, file_name):
        fpath = SNIFFER_DATA_DIR / f"{file_name}.csv"
        df = self._read_csv(fpath)
        df = self._pre_process(df)
        
        return df



