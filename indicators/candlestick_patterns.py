from typing import Tuple
import talib.abstract as ta
import pandas as pd

# We can add more pattern from Talib
patterns = [
    "CDLHANGINGMAN",
    "CDLSHOOTINGSTAR",
    "CDLGRAVESTONEDOJI",
    "CDLHAMMER",
    "CDLINVERTEDHAMMER",
    "CDLDRAGONFLYDOJI",
    "CDLHARAMI",
    "CDLHARAMICROSS",
    "CDLMORNINGSTAR",
    "CDLMORNINGDOJISTAR",
    "CDLSEPARATINGLINES",
    "CDLSTALLEDPATTERN",
    "CDLRISEFALL3METHODS",
    "CDLEVENINGSTAR",
    "CDLEVENINGDOJISTAR",
    "CDLDOJISTAR",
    "CDLADVANCEBLOCK",
]


def find_candlestick_patterns(dataframe: pd.DataFrame) -> Tuple[pd.Series, pd.Series]:
    """
    This function identifies candlestick patterns in a given DataFrame of OHLC (Open, High, Low, Close) data.
    It uses TA-Lib's candlestick pattern recognition functions to detect bullish and bearish candlestick patterns.

    Parameters:
    -----------
    dataframe: pd.DataFrame
        The input DataFrame should contain the following columns:
        - 'open': Opening price for each time period
        - 'high': Highest price for each time period
        - 'low': Lowest price for each time period
        - 'close': Closing price for each time period

    Returns:
    --------
    Tuple[pd.Series, pd.Series]
        - The first element is a pandas Series with a flag (1 or NaN) indicating the presence of a bullish pattern.
        - The second element is a pandas Series with a flag (1 or NaN) indicating the presence of a bearish pattern.

    Notes:
    ------
    - For each row in the DataFrame, the function will check if any bullish or bearish candlestick pattern is detected.
    - TA-Lib pattern functions return 100 for a bullish pattern and -100 for a bearish pattern.
    - If multiple patterns are detected for a given row, they are stored in lists within the DataFrame.
    - If any bullish or bearish pattern is detected, the corresponding flag ('bullish_candle' or 'bearish_candle') will be set to 1.
    """
    df = dataframe.copy()
    # Initialize empty columns
    df["bullish_pattern"] = [[] for _ in range(len(df))]
    df["bearish_pattern"] = [[] for _ in range(len(df))]

    # Loop through each pattern function
    for pattern in patterns:
        # Get the function from TA-Lib
        pattern_function = getattr(ta, pattern)

        # Apply the function to the df
        result = pattern_function(df["open"], df["high"], df["low"], df["close"])

        # Add the pattern name to the appropriate list in each row
        df.loc[result == 100, "bullish_pattern"] = df.loc[
            result == 100, "bullish_pattern"
        ].apply(lambda x: x + [pattern])
        df.loc[result == -100, "bearish_pattern"] = df.loc[
            result == -100, "bearish_pattern"
        ].apply(lambda x: x + [pattern])

    df.loc[df["bullish_pattern"].apply(lambda x: len(x) > 0), "bullish_candle"] = 1
    df.loc[df["bearish_pattern"].apply(lambda x: len(x) > 0), "bearish_candle"] = 1

    return df["bullish_candle"], df["bearish_candle"]
