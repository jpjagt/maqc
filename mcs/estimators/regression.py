import pandas as pd
import numpy as np

from sklearn.model_selection import cross_validate, train_test_split
from sklearn.metrics import mean_squared_error, r2_score


def split_data(df, x_cols, y_col, train_size=0.8, encoder=None):
    df_train, df_test = train_test_split(
        df, train_size=train_size, test_size=(1 - train_size), random_state=5
    )

    if encoder is not None:
        df_train[x_cols] = encoder.encode_X(df_train[x_cols])
        df_train[y_col] = encoder.encode_y(df_train[y_col])
        df_test[x_cols] = encoder.encode_X(df_test[x_cols])
        df_test[y_col] = encoder.encode_y(df_test[y_col])

    X_train = df_train[x_cols].values
    y_train = df_train[y_col].values

    X_test = df_test[x_cols].values
    y_test = df_test[y_col].values

    return X_train, y_train, X_test, y_test, df_train, df_test


class RegressionEstimator(object):
    def __init__(
        self,
        model,
        df,
        x_cols,
        y_col,
        do_cross_validation=True,
        n_folds=5,
        encoder=None,
    ):
        self._model = model
        self._do_cross_validation = do_cross_validation
        self._n_folds = n_folds
        self._encoder = encoder

        self._x_cols = x_cols
        (
            self._X_train,
            self._y_train,
            self._X_test,
            self._y_test,
            self._df_train,
            self._df_test,
        ) = split_data(df, x_cols=x_cols, y_col=y_col, encoder=self._encoder)

    def train(self):
        # fit anyway, even if we're doing cv, because if we're training a
        # pipeline with a preprocessor, that preprocessor needs to be fit,
        # which doesn't happen in cv
        self._model.fit(self._X_train, self._y_train)

        if not self._do_cross_validation:
            return

        results = cross_validate(
            self._model,
            self._X_train,
            self._y_train,
            cv=self._n_folds,
            return_estimator=True,
        )
        coefs = []
        intercepts = []
        for i, model in enumerate(results["estimator"]):
            if hasattr(model, "named_steps"):
                coef = model.named_steps.linearregression.coef_
                intercept = model.named_steps.linearregression.intercept_
            else:
                coef = model.coef_
                intercept = model.intercept_
            coefs.append(coef)
            intercepts.append(intercept)

        mean_coef = np.array(coefs).mean(axis=0)
        mean_intercept = np.array(intercepts).mean(axis=0)
        if hasattr(self._model, "named_steps"):
            self._model.named_steps.linearregression.coef_ = mean_coef
            self._model.named_steps.linearregression.intercept_ = (
                mean_intercept
            )
        else:
            self._model.coef_ = mean_coef
            self._model.intercept_ = mean_intercept

    def predict(self, df):
        df_encoded = self._encoder.encode_X(df)
        y_pred = self._model.predict(df_encoded[self._x_cols].values)
        return self._encoder.decode_y(y_pred)

    def test(self):
        y_pred = self._model.predict(self._X_test)
        y_pred_decoded = self._encoder.decode_y(y_pred)
        y_test_decoded = self._encoder.decode_y(self._y_test)
        r2 = r2_score(y_test_decoded, y_pred_decoded)
        rmse = np.sqrt(mean_squared_error(y_test_decoded, y_pred_decoded))
        print("r2", r2)
        print("RMSE", rmse)
        results_df = pd.DataFrame(
            {
                "y_test": y_test_decoded,
                "y_pred": y_pred_decoded,
            },
            index=self._df_test.index,
        )
        return r2, rmse, results_df
