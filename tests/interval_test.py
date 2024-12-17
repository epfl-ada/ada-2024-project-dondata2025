import numpy as np
import statsmodels.api as sm
import pandas as pd


def outside_interval(predicted, up, down, real_data, tolerance):
    """
    Check if the actual data lies outside the prediction and it's interval and no points are beneath it
    predicted: serie of predicted values
    up: serie of upper bounds
    down: serie of lower bounds
    real_data: serie of real values
    tolerance: percentage of tolerance (<=1)
    """
    # down < predicted < up

    # points outside interval
    outside = (real_data > up) | (real_data < down)

    # real points beneath predicted
    points_beneath = real_data < predicted
    
    # We return true if >tolerance% of the points are outside the interval and no points are beneath the predicted
    return (outside.sum() / len(outside) > tolerance) & (points_beneath.sum() == 0)

    