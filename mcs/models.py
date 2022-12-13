from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline


def get_linear_regression_model():
    return make_pipeline(
        LinearRegression(),
    )


def get_polynomial_regression_model(**kwargs):
    return make_pipeline(
        PolynomialFeatures(**{"degree": 2, **kwargs, "include_bias": False}),
        LinearRegression(),
    )


def get_random_forest_model(**kwargs):
    return make_pipeline(
        RandomForestRegressor(
            **{
                "n_estimators": 200,
                "max_features": "sqrt",
                "min_samples_split": 4,
                "min_samples_leaf": 0.01,
                **kwargs,
            }
        ),
    )
