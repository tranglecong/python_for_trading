import numpy as np
import pandas as pd


def pivot_low(dataframe, left, right):
    """
    Identifies pivot low points in a given DataFrame based on the specified left and right window sizes.

    A pivot low is defined as a point that is lower than all values in the 'left' window before it
    and less than or equal to all values in the 'right' window after it.

    Parameters:
    ----------
    dataframe : pd.DataFrame
        The input DataFrame containing the price data, must include a 'low' column.
    left : int
        The number of preceding values to compare against.
    right : int
        The number of succeeding values to compare against.

    Returns:
    -------
    pd.Series
        A Series containing the identified pivot lows with the original index, where non-pivot points are NaN.
    """

    if "low" not in dataframe.columns:
        raise ValueError("The DataFrame must contain a 'low' column.")

    if (
        not isinstance(left, int)
        or not isinstance(right, int)
        or left <= 0
        or right <= 0
    ):
        raise ValueError("'left' and 'right' must be positive integers.")

    if len(dataframe) < (left + right + 1):
        raise ValueError(
            "The DataFrame is too small for the specified 'left' and 'right' window sizes."
        )

    lows = dataframe["low"]
    pivot_lows = [np.nan] * len(lows)

    for i in range(left, len(lows) - right):
        ref = lows.iloc[i]
        left_window = lows.iloc[i - left : i]
        right_window = lows.iloc[i + 1 : i + right + 1]

        if all(ref < left_window) and all(ref <= right_window):
            pivot_lows[i] = ref

    return pd.Series(pivot_lows, index=dataframe.index)


def pivot_high(dataframe, left, right):
    """
    Identifies pivot high points in a given DataFrame based on the specified left and right window sizes.

    A pivot high is defined as a point that is higher than all values in the 'left' window before it
    and greater than or equal to all values in the 'right' window after it.

    Parameters:
    ----------
    dataframe : pd.DataFrame
        The input DataFrame containing the price data, must include a 'high' column.
    left : int
        The number of preceding values to compare against.
    right : int
        The number of succeeding values to compare against.

    Returns:
    -------
    pd.Series
        A Series containing the identified pivot highs with the original index, where non-pivot points are NaN.
    """

    if "high" not in dataframe.columns:
        raise ValueError("The DataFrame must contain a 'high' column.")

    if (
        not isinstance(left, int)
        or not isinstance(right, int)
        or left <= 0
        or right <= 0
    ):
        raise ValueError("'left' and 'right' must be positive integers.")

    if len(dataframe) < (left + right + 1):
        raise ValueError(
            "The DataFrame is too small for the specified 'left' and 'right' window sizes."
        )

    highs = dataframe["high"]
    pivot_highs = [np.nan] * len(highs)

    for i in range(left, len(highs) - right):
        ref = highs.iloc[i]
        left_window = highs.iloc[i - left : i]
        right_window = highs.iloc[i + 1 : i + right + 1]

        if all(ref > left_window) and all(ref >= right_window):
            pivot_highs[i] = ref

    return pd.Series(pivot_highs, index=dataframe.index)
