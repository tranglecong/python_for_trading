import pandas as pd
import talib.abstract as ta
import technical.vendor.qtpylib.indicators as qtpylib

from indicators.candlestick_patterns import find_candlestick_patterns
from indicators.hawkeye_volume import hawkeye_volume
from indicators.pivot import pivot_high, pivot_low
from ploting.plotting import generate_candlestick_graph, store_plot_file
from utils.logger import logger
from utils.utils import (
    dataframe_date_to_date,
    load_dataframe,
)


def populate_indicators(dataframe: pd.DataFrame) -> pd.DataFrame:
    # RSI
    dataframe["rsi"] = ta.RSI(dataframe, timeperiod=14)

    # ADX
    dataframe["adx"] = ta.ADX(dataframe, timeperiod=14)

    # Parabolic SAR
    dataframe["sar"] = ta.SAR(dataframe, acceleration=0.02, maximum=0.2)

    # Hawkeye Volume
    dataframe["durchschnitt"], dataframe["v_color"] = hawkeye_volume(
        dataframe=dataframe
    )

    # Pivot high/low
    dataframe["pivot_highs"] = pivot_high(dataframe=dataframe, left=10, right=2)
    dataframe["pivot_lows"] = pivot_low(dataframe=dataframe, left=10, right=2)

    dataframe["pivot_lows"] = dataframe["pivot_lows"].ffill()
    dataframe["pivot_highs"] = dataframe["pivot_highs"].ffill()

    # Candlestick pattern
    dataframe["bullish_candle"], dataframe["bearish_candle"] = (
        find_candlestick_patterns(dataframe=dataframe)
    )

    # EMA
    dataframe["ema34"] = ta.EMA(dataframe, timeperiod=34)
    dataframe["ema89"] = ta.EMA(dataframe, timeperiod=89)
    dataframe["ema200"] = ta.EMA(dataframe, timeperiod=200)

    # Bollinger Bands
    bollinger = qtpylib.bollinger_bands(
        qtpylib.typical_price(dataframe), window=20, stds=2
    )
    dataframe["bb_lowerband"] = bollinger["lower"]
    dataframe["bb_middleband"] = bollinger["mid"]
    dataframe["bb_upperband"] = bollinger["upper"]
    dataframe["bb_percent"] = (dataframe["close"] - dataframe["bb_lowerband"]) / (
        dataframe["bb_upperband"] - dataframe["bb_lowerband"]
    )
    dataframe["bb_width"] = (
        dataframe["bb_upperband"] - dataframe["bb_lowerband"]
    ) / dataframe["bb_middleband"]

    dataframe.loc[
        (
            (dataframe["high"] > dataframe["pivot_highs"])
            & (dataframe["bearish_candle"] == 1)
            & (dataframe["open"] < dataframe["pivot_highs"])
            & (dataframe["adx"] > 25)
            & (dataframe["rsi"] > 60)
        ),
        "enter_short",
    ] = 1

    dataframe.loc[
        (
            (dataframe["low"] < dataframe["pivot_lows"])
            & (dataframe["bullish_candle"] == 1)
            & (dataframe["open"] > dataframe["pivot_lows"])
            & (dataframe["adx"] > 25)
            & (dataframe["rsi"] <= 40)
        ),
        "enter_long",
    ] = 1

    dataframe.loc[
        (
            (dataframe["high"] <= dataframe["sar"])
            & (dataframe["low"].shift(1) > dataframe["sar"].shift(1))
            & (dataframe["volume"] > 0)
        ),
        ["exit_long", "exit_tag"],
    ] = 1, "Exit Long - SAR"

    dataframe.loc[
        (
            (dataframe["low"] >= dataframe["sar"])
            & (dataframe["high"].shift(1) < dataframe["sar"].shift(1))
            & (dataframe["volume"] > 0)
        ),
        ["exit_short", "exit_tag"],
    ] = 1, "Exit Short - SAR"

    return dataframe


if __name__ == "__main__":
    logger.info("Trading To The Moon!")
    loaded_dataframe = load_dataframe("./data/BTC_USDT_USDT-1h-futures.feather")

    dataframe = dataframe_date_to_date(
        loaded_dataframe, start_date="20240801", end_date="20240901"
    )

    dataframe = populate_indicators(dataframe=dataframe)

    plot_config = {
        "main_plot": {
            "sar": {
                "plotly": {"mode": "markers", "marker": {"color": "DarkSlateGrey"}}
            },
            "pivot_highs": {
                "plotly": {"mode": "markers", "marker": {"color": "#ff5733"}}
            },
            "pivot_lows": {
                "plotly": {"mode": "markers", "marker": {"color": "#40A677"}}
            },
            "Bollinger Bands": {
                "type": "area",
                "indicator_a": "bb_upperband",
                "indicator_b": "bb_lowerband",
                "fill_color": "rgba(0,176,246,0.2)",
            },
            "bb_middleband": {"color": "#DCD743"},
        },
        "subplots": {
            "RSI": {"rsi": {"color": "#55CE82"}},
            "Hawkeye Volume": {
                "volume": {"type": "bar", "colors": "v_color"},
                "durchschnitt": {"color": "orange"},
            },
        },
    }

    fig = generate_candlestick_graph(
        title="BTCUSDT", data=dataframe, plot_config=plot_config
    )
    store_plot_file(
        fig=fig,
        filename="BTCUSDT-1H-Candlestick-Graph.html",
        directory="./plot",
        auto_open=True,
    )
