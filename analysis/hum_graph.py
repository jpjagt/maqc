from mcs.data_loaders import MITDataLoader
import pandas as pd 
import matplotlib.pyplot as plt
from mcs.plot import plot_line
from sklearn.linear_model import LinearRegression, LogisticRegression 
from sklearn.metrics import mean_squared_error, r2_score
import numpy as np

loader = MITDataLoader()
sensor_df =  loader.load_data("ensemble-site", "ams1")

#convert data type 
sensor_df['PM25']= sensor_df['PM25'].astype(float)

#filter out outliers
sensor_df = sensor_df[sensor_df['PM25'] < sensor_df['PM25'].quantile(.95)] 


#create variables
X=sensor_df[['humidity']]
Y=sensor_df[['PM25']]


#fit second degree polynomial model
lr = LinearRegression()
lg = LogisticRegression()

lr.fit(X**2, Y)

y_pred = lr.predict(X+X**2) 

#plot humidity vs pm25 with fitted line
plt.scatter(X, Y, color = 'red', s = 1)
plt.plot(X, lr.predict(X+X**2), color = 'blue')
plt.title('PM25 vs Humidity')
plt.xlabel('Humidity')
plt.ylabel('PM25')
plt.show()

#Model performance 
r2_score(Y, y_pred)
mean_squared_error(Y, y_pred)
