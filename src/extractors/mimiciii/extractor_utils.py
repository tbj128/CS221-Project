import numpy as np


def calculate_trend(tuples):
    """
    Given an array of tuples of (offset, val), perform least squares to find trend
    """
    if len(tuples) <= 1:
        return 0
    x = np.array([t[0] for t in tuples])
    y = np.array([t[1] for t in tuples])

    return ((np.mean(x) * np.mean(y)) - np.mean(x * y)) / ((np.mean(x) ** 2) - np.mean(x ** 2))
