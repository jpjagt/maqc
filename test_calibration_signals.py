import seaborn as sns
from mcs.constants import DCMR_DATA_DIR
from mcs.data_loaders import MITDataLoader
from mcs import plot
import pandas as pd

mit_df = pd.concat(
    {
        name: MITDataLoader().load_data("final-city-scanner-data", name)
        for name in ["ams3", "ams4"]
    }
)

dcmr_df = pd.read_excel(
    DCMR_DATA_DIR / "schiedam-december-2022" / "pm25-10sec.xlsx", skiprows=1
).rename(columns={"494SDM - PM2.5.L": "pm25_dcmr", "J335 S49": "timestamp"})
dcmr_df.timestamp = pd.to_datetime(dcmr_df.timestamp)
dcmr_df = dcmr_df.set_index("timestamp")


rel_mit_df = (
    mit_df.unstack(level=0)
    .loc["2022-11-29 11:00:00":, ["PM25", "humidity"]]
    .resample("10s")
    .mean()
)
rel_mit_df.columns = [
    "_".join(col).lower() for col in rel_mit_df.columns.values
]
rel_mit_df["mit_pm25_mean"] = rel_mit_df[["pm25_ams3", "pm25_ams4"]].mean(1)
rel_mit_df["mit_humidity_mean"] = rel_mit_df[
    ["humidity_ams3", "humidity_ams4"]
].mean(1)

rel_mit_df = rel_mit_df.asfreq("10s")
rel_mit_df["pm25_dcmr"] = dcmr_df["pm25_dcmr"]
rel_mit_df.plot(alpha=0.5)
plot.plt.legend()
plot.plt.show()

rel_mit_df["mit_pm25_is_outlier"] = (
    rel_mit_df["mit_pm25_mean"] < rel_mit_df["mit_pm25_mean"].quantile(0.00)
) | (rel_mit_df["mit_pm25_mean"] > rel_mit_df["mit_pm25_mean"].quantile(0.95))

rel_mit_df["mit_humidity_mean_rounded"] = rel_mit_df[
    "mit_humidity_mean"
].round(-1)

sns.scatterplot(
    data=rel_mit_df,
    x="mit_pm25_mean",
    y="pm25_dcmr",
    style="mit_pm25_is_outlier",
    hue="mit_humidity_mean_rounded",
)
plot.plt.legend()
plot.plt.show()
