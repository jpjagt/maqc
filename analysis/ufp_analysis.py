from mcs.data_loaders import UFPDataLoader
from matplotlib import pyplot as plt

ufp_df = UFPDataLoader().load_data("test", "ufp1")
print(ufp_df)

# to be modified depending on analysis
# ufp_df.set_index("timestamp").asfreq("S").ffill().resample("M").mean().number.plot()
# plt.show()

ufp_df[["timestamp", "src_fname"]].value_counts()
mask = ufp_df.timestamp.duplicated(keep=False)
ufp_df[mask].groupby("timestamp").number.unique()
