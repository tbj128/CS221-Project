import sys

from math import sqrt
from pandas import read_csv
from sklearn.linear_model import SGDClassifier, SGDRegressor, LogisticRegression, LinearRegression
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

input_file = sys.argv[1]
use_demography = sys.argv[2]
use_trends = sys.argv[3]

df = read_csv(input_file, header=0, index_col=0)
values = df.values

if use_demography == "true":
    encoder = LabelEncoder()
    values[:, 2] = encoder.fit_transform(values[:, 2]) # gender
    values[:, 3] = encoder.fit_transform(values[:, 3]) # insurance
    values[:, 4] = encoder.fit_transform(values[:, 4]) # language
    values[:, 5] = encoder.fit_transform(values[:, 5]) # religion
    values[:, 6] = encoder.fit_transform(values[:, 6]) # marital
    values[:, 7] = encoder.fit_transform(values[:, 7]) # ethnicity
else:
    df = df.drop(df.columns[[2, 3, 4, 5, 6, 7]], axis=1)
    values = df.values

if use_trends != "true":
    df = df.filter(regex='(?!-trend)')
    values = df.values


# ensure all data is float
values = values.astype('float64')

X = values[:, 1:]
y = values[:, 0]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.70)

# clf = SGDRegressor(loss="squared_loss", penalty="l1", eta0=0.0001)
clf = LinearRegression(normalize=True)
clf.fit(X_train, y_train)

y_preds = clf.predict(X_train)
training_error = mean_squared_error(y_train, y_preds)
print("Training (LOS): " + str(sqrt(training_error)))

y_preds = clf.predict(X_test)
test_error = mean_squared_error(y_test, y_preds)
print("Testing (LOS): " + str(sqrt(test_error)))
