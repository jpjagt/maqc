from mcs.data_loaders import KNMIDataLoader
from mcs.data_loaders import MITDataLoader
from mcs.utils import get_ts_dfknmi
from matplotlib import pyplot as plt
from windrose import WindroseAxes

knmi_df = KNMIDataLoader().load_data()
mit1_df = MITDataLoader().load_data("ensemble-site", "ams1")
mit1_df = mit1_df.loc["2022-11-01":, :]
print(mit1_df.head())

knmi_df = get_ts_dfknmi(knmi_df, ts_col="Date", resample_to=None)
knmi_df = knmi_df.join(mit1_df['PM25'])

#generate windrose
fig, ax = plt.subplots(figsize=(8, 8), dpi=80)
ax = WindroseAxes.from_ax()
ax.bar(knmi_df.Avg_Wind_Direction, knmi_df.Avg_Windspeed, normed=True, opening=0.8, edgecolor='white')
ax.set_legend()
plt.show()

