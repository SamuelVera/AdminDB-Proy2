import sys
import pandas as pd
import psycopg2 as pg2
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn import datasets

    #DATASET
boston = datasets.load_boston()

    #TRANSFORM TO DATAFRAME
bos = pd.DataFrame(boston.data)

    #COLUMN NAME
bos.columns = boston.feature_names

    #TRAINING DATA
X = bos #FEATURES
Y = boston.target #TARGET

lreg = LinearRegression()

lreg.fit(X, Y)

print(lreg.predict(X)[0:5])