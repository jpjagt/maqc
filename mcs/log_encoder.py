import numpy as np


class LogEncoder(object):
    def __init__(self, x_cols_to_encode):
        self._x_cols_to_encode = x_cols_to_encode

    def encode_X(self, df):
        df = df.copy()
        df[self._x_cols_to_encode] = np.log(df[self._x_cols_to_encode])
        return df

    def encode_y(self, series):
        return np.log(series)

    def decode_X(self, df):
        df = df.copy()
        df[self._x_cols_to_encode] = np.exp(df[self._x_cols_to_encode])
        return df

    def decode_y(self, series):
        return np.exp(series)
