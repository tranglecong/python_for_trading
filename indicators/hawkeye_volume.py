from typing import Tuple

import numpy as np
import pandas as pd
import technical.qtpylib as qtpylib


def hawkeye_volume(
    dataframe: pd.DataFrame, length: int = 200, hv_ma: int = 20, divisor: float = 3.6
) -> Tuple[pd.Series, pd.Series]:
    """
    Calculate the Hawkeye Volume indicator based on the given DataFrame.
    This indicator applies specific rules to classify volume bars into red, green, gray, and blue,
    with corresponding logic for detecting volume behavior in relation to price ranges and averages.

    :param dataframe: A DataFrame containing OHLCV data (Open, High, Low, Close, Volume).
    :param length: The window length for calculating long-term moving averages (default is 200).
    :param hv_ma: The window length for calculating short-term moving averages (default is 20).
    :param divisor: A divisor value used for calculating upper and lower bounds of the price range (default is 3.6).
    :return: A tuple of (volume moving average, volume color series).
    """
    df = dataframe.copy()
    # Calculate the moving average of volume
    df["range"] = df["high"] - df["low"]
    df["rangeAvg"] = qtpylib.sma(df["range"], window=length)
    df["durchschnitt"] = qtpylib.sma(df["volume"], window=hv_ma)
    df["volumeA"] = qtpylib.sma(df["volume"], window=length)
    df["mid"] = qtpylib.mid_price(df)

    df["u"] = df["mid"] + (df["high"] - df["low"]) / divisor
    df["d"] = df["mid"] - (df["high"] - df["low"]) / divisor

    # Define conditions based on the Pine Script logic
    df["r_enabled1"] = (
        (df["range"] > df["rangeAvg"])
        & (df["close"] < df["d"].shift(1))
        & (df["volume"] > df["volumeA"])
    )
    df["r_enabled2"] = df["close"] < df["mid"].shift(1)
    df["r_enabled"] = df["r_enabled1"] | df["r_enabled2"]

    df["g_enabled1"] = df["close"] > df["mid"].shift(1)
    df["g_enabled2"] = (
        (df["range"] > df["rangeAvg"])
        & (df["close"] > df["u"].shift(1))
        & (df["volume"] > df["volumeA"])
    )
    df["g_enabled3"] = (
        (df["high"] > df["high"].shift(1))
        & (df["range"] < df["rangeAvg"] / 1.5)
        & (df["volume"] < df["volumeA"])
    )
    df["g_enabled4"] = (
        (df["low"] < df["low"].shift(1))
        & (df["range"] < df["rangeAvg"] / 1.5)
        & (df["volume"] > df["volumeA"])
    )
    df["g_enabled"] = (
        df["g_enabled1"] | df["g_enabled2"] | df["g_enabled3"] | df["g_enabled4"]
    )

    df["gr_enabled1"] = (
        (df["range"] > df["rangeAvg"])
        & (df["close"] > df["d"].shift(1))
        & (df["close"] < df["u"].shift(1))
        & (df["volume"] > df["volumeA"])
        & (df["volume"] < df["volumeA"] * 1.5)
        & (df["volume"] > df["volume"].shift(1))
    )
    df["gr_enabled2"] = (df["range"] < df["rangeAvg"] / 1.5) & (
        df["volume"] < df["volumeA"] / 1.5
    )
    df["gr_enabled3"] = (df["close"] > df["d"].shift(1)) & (
        df["close"] < df["u"].shift(1)
    )
    df["gr_enabled"] = df["gr_enabled1"] | df["gr_enabled2"] | df["gr_enabled3"]

    # Set the color based on the conditions
    df["v_color"] = np.where(
        df["gr_enabled"],
        "gray",
        np.where(
            df["g_enabled"],
            "#3D9970",
            np.where(df["r_enabled"], "#FF4136", "blue"),
        ),
    )

    return df["durchschnitt"], df["v_color"]
