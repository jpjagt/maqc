from mcs.data_loaders import UFPDataLoader
from matplotlib import pyplot as plt
from mcs import plot

loader = UFPDataLoader()
df1 = loader.load_data("2022_11_24", "sensor1")
df2 = loader.load_data("2022_11_24", "sensor2")

# to be modified depending on analysis
# ufp_df.set_index("timestamp").asfreq("S").ffill().resample("M").mean().number.plot()
# plt.show()

# ufp_df[["timestamp", "src_fname"]].value_counts()
# mask = ufp_df.timestamp.duplicated(keep=False)
# ufp_df[mask].groupby("timestamp").number.unique()

# general comparison
plot.plot_line(
    [df1, df2],
    "mass",
    xlabel="time",
    ylabel="PM0.3 micrograms/m3",
    legend=["sensor1", "sensor2"],
    outliers=(0, 0.99),
)

# experiments when they weren't co-located
plot.plot_line(
    [
        df1["2022-11-24 06:47:00":"2022-11-24 07:13:00"],
        df2["2022-11-24 06:47:00":"2022-11-24 07:13:00"],
    ],
    "mass",
    xlabel="time",
    ylabel="PM0.3 micrograms/m3",
    legend=["sensor1", "sensor2"],
    outliers=(0, 0.99),
)

# before construction started vs when started
plot.plot_line(
    [
        df1["2022-11-24 06:18:00":"2022-11-24 06:47:00"],
        df2["2022-11-24 06:18:00":"2022-11-24 06:47:00"],
    ],
    "mass",
    xlabel="time",
    ylabel="PM0.3 micrograms/m3",
    legend=["sensor1", "sensor2"],
    outliers=(0, 0.99),
)

# mean particle counts
# coffee break 9:30-10:00 (13991)
df2[df2["number"] < 1e6]["number"][
    "2022-11-24 09:30:00":"2022-11-24 10:00:00"
].mean()
# after break 10:00-11:00 (43040)
df2[df2["number"] < 1e6]["number"][
    "2022-11-24 10:00:00":"2022-11-24 11:00:00"
].mean()
# before the break 9:00-9:30 (25897)
df2[df2["number"] < 1e6]["number"][
    "2022-11-24 9:00:00":"2022-11-24 09:30:00"
].mean()
