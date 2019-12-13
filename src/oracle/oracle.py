"""
Linear regression with SGD for the oracle model. This model performs regression using the
number of days that a prescription was prescribed for a proxy to predict the actual LOS.

Oracles act as a "upper-bound" performance for our model by peeking at information
that it normally shouldn't have access to.

Note: extract_oracle_data.py must be run prior to running this file

"""
import csv

from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.metrics import mean_squared_error, mean_absolute_error
from sklearn.model_selection import train_test_split
import random
from sklearn import metrics

X = []
y = []
y_status = []

FILENAME = "../../data/exp/ORACLE.csv"

with open(FILENAME) as f:
    num_lines = sum(1 for line in f)
    num_training = round(0.7 * num_lines)

with open(FILENAME, 'r') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    i = 0
    for row in csv_reader:
        age = float(row[0])
        gender = float(row[1])
        expired = float(row[2])
        num_days_prescription = float(row[4])
        los = float(row[5])
        status = row[6]
        # X.append([age, gender, expired, num_days_prescription])
        X.append([num_days_prescription])
        y.append(los)
        y_status.append(status)
        i += 1

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.70)

# clf = SGDRegressor(loss="squared_loss", penalty="l1", eta0=0.0000001)
clf = LinearRegression()
clf.fit(X_train, y_train)

y_preds = clf.predict(X_train)
training_error = mean_absolute_error(y_train, y_preds)
print("Training (LOS): " + str(training_error))

y_preds = clf.predict(X_test)
test_error = mean_absolute_error(y_test, y_preds)
print("Testing (LOS): " + str(test_error))

# y_preds = clf.predict([[10, 1, 10] for _ in range(len(y_test))])
# test_error = mean_squared_error(y_test, y_preds)
# print("Testing (LOS - RANDOM): " + str(test_error))

##########


# Resample to ensure even classification
X_alive = []
X_expired = []
y_alive = []
y_expired = []
i = 0
while i < len(X):
    if y_status[i] != "1":
        X_expired.append(X[i])
        y_expired.append(y_status[i])
    else:
        X_alive.append(X[i])
        y_alive.append(y_status[i])
    i += 1

print("Number of alive: " + str(len(X_alive)))
print("Number of expired: " + str(len(X_expired)))

sampled_indices = random.sample([i for i in range(len(X_alive))], len(y_expired))
X_alive_sampled = [X_alive[i] for i in sampled_indices]
y_alive_sampled = [y_alive[i] for i in sampled_indices]

print("Number of sampled alive: " + str(len(X_alive_sampled)))

# Join the data back
X_sampled = []
y_sampled = []
X_sampled.extend(X_alive_sampled)
y_sampled.extend(y_alive_sampled)
X_sampled.extend(X_expired)
y_sampled.extend(y_expired)

print("Number of joined: " + str(len(X_sampled)))

# Split train/test
X_train, X_test, y_train, y_test = train_test_split(X_sampled, y_sampled, test_size=0.70)

# clf = SGDClassifier(loss="hinge", penalty="l1", eta0=0.0001)
clf = LogisticRegression()
clf.fit(X_train, y_train)

y_preds = clf.predict(X_train)
correct = 0
i = 0
for y_pred in y_preds:
    if y_pred == y_train[i]:
        correct += 1
    i += 1
print("Training (STATUS): " + str(correct / float(len(y_preds))))

y_preds = clf.predict(X_test)
correct = 0
i = 0
for y_pred in y_preds:
    if y_pred == y_test[i]:
        correct += 1
    i += 1
print("Testing (STATUS): " + str(correct / float(len(y_preds))))


y_test = list(map(int, y_test))
y_preds = list(map(int, y_preds))
fpr, tpr, thresholds = metrics.roc_curve(y_test, y_preds)
print("AUC: " + str(metrics.auc(fpr, tpr)))

