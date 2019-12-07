"""
Filters matrix to remove columns that occur with a less than X%, replaces empty or inf values with 0

Used when filtering the 24/48 hour files

"""

import sys
from pandas import read_csv, np

input_file = sys.argv[1]
df = read_csv(input_file, header=0)
df = df.loc[:, (df==0).mean() < .7]
df.fillna(0, inplace=True)
df = df.replace([np.inf, -np.inf], 0)
print(df.head(5))
df.to_csv(input_file + ".filtered.csv")
