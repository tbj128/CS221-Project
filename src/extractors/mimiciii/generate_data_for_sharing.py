"""
Due to the restricted-access nature of the dataset, we are unable to share the file
used for training. However, this script creates a training file that is representative
of the original dataset.

"""

import pandas as pd
import numpy as np

print("Producing randomly sampled data")

# raw_dataset = pd.read_csv('../../../data/exp/pneumonia-t3/first48hours.filtered.csv', header=0, index_col=0)
# df = raw_dataset.copy()
#
# new_df = pd.DataFrame(columns=df.columns)
# for i in range(len(df)):
#     row = []
#     for col in df.columns:
#         row.append(np.random.choice(df[col]))
#     new_df.loc[i] = row
#
# new_df.to_csv('../../../data/exp/pneumonia-t3/example.first48hours.filtered.csv')


raw_dataset = pd.read_csv('../../../data/exp/pneumonia-t3/timestep.filtered.csv', header=0, index_col=0)
df = raw_dataset.copy()

new_df = pd.DataFrame(columns=df.columns)
for i in range(len(df)):
    row = []
    for col in df.columns:
        row.append(np.random.choice(df[col]))
    new_df.loc[i] = row
    if i % 100 == 0:
        print("Completed " + str(i))

new_df.to_csv('../../../data/exp/pneumonia-t3/example.timestep.filtered.csv')
