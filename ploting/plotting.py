from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd
import plotly.graph_objects as go
from plotly.offline import plot
from plotly.subplots import make_subplots
from tqdm import tqdm

from utils.logger import logger


def create_scatter(data, column_name, color, direction) -> Optional[go.Scatter]:
    if column_name in data.columns:
        df_short = data[data[column_name] == 1]
        if len(df_short) > 0:
            shorts = go.Scatter(
                x=df_short.date,
                y=df_short.close,
                mode="markers",
                name=column_name,
                marker=dict(
                    symbol=f"triangle-{direction}-dot",
                    size=9,
                    line=dict(width=1),
                    color=color,
                ),
            )
            return shorts
        else:
            logger.debug(f"No {column_name}-signals found.")

    return None


def add_indicators(
    fig, row, indicators: Dict[str, Dict], data: pd.DataFrame
) -> make_subplots:
    """
    Generate all the indicators selected by the user for a specific row, based on the configuration
    :param fig: Plot figure to append to
    :param row: row number for this plot
    :param indicators: Dict of Indicators with configuration options.
                       Dict key must correspond to dataframe column.
    :param data: candlestick DataFrame
    """
    plot_kinds = {
        "scatter": go.Scatter,
        "bar": go.Bar,
    }
    for indicator, conf in indicators.items():
        logger.debug(f"indicator {indicator} with config {conf}")
        if indicator in data:
            kwargs = {"x": data["date"], "y": data[indicator].values, "name": indicator}

            plot_type = conf.get("type", "scatter")
            color = conf.get("color")
            if plot_type == "bar":
                marker_colors = color if color else "DarkSlateGrey"
                if (
                    "volume" in indicator
                    or "Volume" in indicator
                    or "Vol" in indicator
                    or "vol" in indicator
                ):
                    marker_colors = [
                        "#3D9970" if close > open else "#FF4136"
                        for open, close in zip(data.open, data.close)
                    ]
                colors = conf.get("colors")
                marker_colors = (
                    data[colors] if colors in data.columns else marker_colors
                )
                kwargs.update(
                    {"marker_color": marker_colors, "marker_line_color": marker_colors}
                )
            else:
                if color:
                    kwargs.update({"line": {"color": color}})
                kwargs["mode"] = "lines"
                if plot_type != "scatter":
                    logger.debug(
                        f"Indicator {indicator} has unknown plot trace kind {plot_type}"
                        f', assuming "scatter".'
                    )

            kwargs.update(conf.get("plotly", {}))
            trace = plot_kinds[plot_type](**kwargs)
            fig.add_trace(trace, row, 1)
        else:
            plot_type = conf.get("type")
            if plot_type == "area":
                if "indicator_a" in conf and "indicator_b" in conf:
                    fill_color = (
                        conf["fill_color"]
                        if "fill_color" in conf
                        else "rgba(0,176,246,0.2)"
                    )
                    fig = plot_area(
                        fig,
                        1,
                        data,
                        conf["indicator_a"],
                        conf["indicator_b"],
                        label=indicator,
                        fill_color=fill_color,
                    )
            logger.debug(
                'Indicator "%s" ignored. Reason: This indicator is not found '
                "in your strategy.",
                indicator,
            )

    return fig


def plot_trades(fig, trades: pd.DataFrame) -> make_subplots:
    """
    Add trades to "fig"
    """
    # Trades can be empty
    if trades is not None and len(trades) > 0:
        # Create description for exit summarizing the trade
        trades["desc"] = trades.apply(
            lambda row: f"{row['profit_ratio']:.2%}, "
            + (f"{row['enter_tag']}, " if row["enter_tag"] is not None else "")
            + f"{row['exit_reason']}, "
            + f"{row['trade_duration']} min",
            axis=1,
        )
        trade_entries = go.Scatter(
            x=trades["open_date"],
            y=trades["open_rate"],
            mode="markers",
            name="Trade entry",
            text=trades["desc"],
            marker=dict(
                symbol="circle-open", size=11, line=dict(width=2), color="cyan"
            ),
        )

        trade_exits = go.Scatter(
            x=trades.loc[trades["profit_ratio"] > 0, "close_date"],
            y=trades.loc[trades["profit_ratio"] > 0, "close_rate"],
            text=trades.loc[trades["profit_ratio"] > 0, "desc"],
            mode="markers",
            name="Exit - Profit",
            marker=dict(
                symbol="square-open", size=11, line=dict(width=2), color="green"
            ),
        )
        trade_exits_loss = go.Scatter(
            x=trades.loc[trades["profit_ratio"] <= 0, "close_date"],
            y=trades.loc[trades["profit_ratio"] <= 0, "close_rate"],
            text=trades.loc[trades["profit_ratio"] <= 0, "desc"],
            mode="markers",
            name="Exit - Loss",
            marker=dict(symbol="square-open", size=11, line=dict(width=2), color="red"),
        )
        fig.add_trace(trade_entries, 1, 1)
        fig.add_trace(trade_exits, 1, 1)
        fig.add_trace(trade_exits_loss, 1, 1)
    else:
        logger.debug("No trades found.")
    return fig


def plot_area(
    fig,
    row: int,
    data: pd.DataFrame,
    indicator_a: str,
    indicator_b: str,
    label: str = "",
    fill_color: str = "rgba(0,176,246,0.2)",
) -> make_subplots:
    """Creates a plot for the area between two traces and adds it to fig.
    :param fig: Plot figure to append to
    :param row: row number for this plot
    :param data: candlestick DataFrame
    :param indicator_a: indicator name as populated in strategy
    :param indicator_b: indicator name as populated in strategy
    :param label: label for the filled area
    :param fill_color: color to be used for the filled area
    :return: fig with added  filled_traces plot
    """
    if indicator_a in data and indicator_b in data:
        # make lines invisible to get the area plotted, only.
        line = {"color": "rgba(255,255,255,0)"}
        # TODO: Figure out why scattergl causes problems plotly/plotly.js#2284
        trace_a = go.Scatter(
            x=data.date, y=data[indicator_a], showlegend=False, line=line
        )
        trace_b = go.Scatter(
            x=data.date,
            y=data[indicator_b],
            name=label,
            fill="tonexty",
            fillcolor=fill_color,
            line=line,
        )
        fig.add_trace(trace_a, row, 1)
        fig.add_trace(trace_b, row, 1)
    return fig


def add_areas(fig, row: int, data: pd.DataFrame, indicators) -> make_subplots:
    """Adds all area plots (specified in plot_config) to fig.
    :param fig: Plot figure to append to
    :param row: row number for this plot
    :param data: candlestick DataFrame
    :param indicators: dict with indicators. ie.: plot_config['main_plot'] or
                            plot_config['subplots'][subplot_label]
    :return: fig with added  filled_traces plot
    """
    for indicator, ind_conf in indicators.items():
        if "fill_to" in ind_conf:
            indicator_b = ind_conf["fill_to"]
            if indicator in data and indicator_b in data:
                label = ind_conf.get("fill_label", f"{indicator}<>{indicator_b}")
                fill_color = ind_conf.get("fill_color", "rgba(0,176,246,0.2)")
                fig = plot_area(
                    fig,
                    row,
                    data,
                    indicator,
                    indicator_b,
                    label=label,
                    fill_color=fill_color,
                )
            elif indicator not in data:
                logger.debug(
                    'Indicator "%s" ignored. Reason: This indicator is not '
                    "found in your strategy.",
                    indicator,
                )
            elif indicator_b not in data:
                logger.debug(
                    'fill_to: "%s" ignored. Reason: This indicator is not '
                    "in your strategy.",
                    indicator_b,
                )
    return fig


def create_plotconfig(
    indicators1: List[str], indicators2: List[str], plot_config: Dict[str, Dict]
) -> Dict[str, Dict]:
    """
    Combines indicators 1 and indicators 2 into plot_config if necessary
    :param indicators1: List containing Main plot indicators
    :param indicators2: List containing Sub plot indicators
    :param plot_config: Dict of Dicts containing advanced plot configuration
    :return: plot_config - eventually with indicators 1 and 2
    """

    if plot_config:
        if indicators1:
            plot_config["main_plot"] = {ind: {} for ind in indicators1}
        if indicators2:
            plot_config["subplots"] = {"Other": {ind: {} for ind in indicators2}}

    if not plot_config:
        # If no indicators and no plot-config given, use defaults.
        if not indicators1:
            indicators1 = ["sma", "ema3", "ema5"]
        if not indicators2:
            indicators2 = ["macd", "macdsignal"]

        # Create subplot configuration if plot_config is not available.
        plot_config = {
            "main_plot": {ind: {} for ind in indicators1},
            "subplots": {"Other": {ind: {} for ind in indicators2}},
        }
    if "main_plot" not in plot_config:
        plot_config["main_plot"] = {}

    if "subplots" not in plot_config:
        plot_config["subplots"] = {}
    return plot_config


def generate_candlestick_graph(
    title: str,
    data: pd.DataFrame,
    trades: Optional[pd.DataFrame] = None,
    *,
    indicators1: Optional[List[str]] = None,
    indicators2: Optional[List[str]] = None,
    plot_config: Optional[Dict[str, Dict]] = None,
) -> go.Figure:
    """
    Generate the graph from the data generated by Backtesting or from DB
    Volume will always be plotted in row2, so Row 1 and 3 are to our disposal for custom indicators
    :param title: Title to Display on the graph
    :param data: OHLCV DataFrame containing indicators and entry/exit signals
    :param trades: All trades created
    :param indicators1: List containing Main plot indicators
    :param indicators2: List containing Sub plot indicators
    :param plot_config: Dict of Dicts containing advanced plot configuration
    :return: Plotly figure
    """
    plot_config = create_plotconfig(
        indicators1 or [],
        indicators2 or [],
        plot_config or {},
    )
    rows = 1 + len(plot_config["subplots"])
    row_widths = [1 for _ in plot_config["subplots"]]
    # Define the graph
    fig = make_subplots(
        rows=rows,
        cols=1,
        shared_xaxes=True,
        row_width=row_widths + [4],
        vertical_spacing=0.0001,
    )
    fig["layout"].update(title=title)
    fig["layout"]["yaxis1"].update(title="Price")
    # fig["layout"]["yaxis2"].update(title="Volume")
    for i, name in enumerate(plot_config["subplots"]):
        fig["layout"][f"yaxis{2 + i}"].update(title=name)
    fig["layout"]["xaxis"]["rangeslider"].update(visible=False)
    fig.update_layout(modebar_add=["v1hovermode", "toggleSpikeLines"])

    # Common information
    candles = go.Candlestick(
        x=data.date,
        open=data.open,
        high=data.high,
        low=data.low,
        close=data.close,
        name="Price",
        increasing={"fillcolor": "#3D9970"},
        decreasing={"fillcolor": "#FF4136"},
    )
    fig.add_trace(candles, 1, 1)

    longs = create_scatter(data, "enter_long", "green", "up")
    exit_longs = create_scatter(data, "exit_long", "red", "down")
    shorts = create_scatter(data, "enter_short", "blue", "down")
    exit_shorts = create_scatter(data, "exit_short", "violet", "up")

    for scatter in [longs, exit_longs, shorts, exit_shorts]:
        if scatter:
            fig.add_trace(scatter, 1, 1)

    # Add Bollinger Bands
    fig = plot_area(
        fig, 1, data, "bb_lowerband", "bb_upperband", label="Bollinger Band"
    )
    # prevent bb_lower and bb_upper from plotting
    try:
        del plot_config["main_plot"]["bb_lowerband"]
        del plot_config["main_plot"]["bb_upperband"]
    except KeyError:
        pass
    # main plot goes to row 1
    fig = add_indicators(fig=fig, row=1, indicators=plot_config["main_plot"], data=data)
    fig = add_areas(fig, 1, data, plot_config["main_plot"])
    fig = plot_trades(fig, trades)
    # sub plot: Volume goes to row 2
    # volume_colors = [
    #     "#3D9970" if close > open else "#FF4136"
    #     for open, close in zip(data.open, data.close)
    # ]
    # volume = go.Bar(
    #     x=data["date"],
    #     y=data["volume"],
    #     name="Volume",
    #     marker_color=volume_colors,
    #     marker_line_color=volume_colors,
    # )
    # fig.add_trace(volume, 2, 1)
    # add each sub plot to a separate row
    for i, label in enumerate(plot_config["subplots"]):
        sub_config = plot_config["subplots"][label]
        row = 2 + i
        fig = add_indicators(fig=fig, row=row, indicators=sub_config, data=data)
        # fill area between indicators ( 'fill_to': 'other_indicator')
        fig = add_areas(fig, row, data, sub_config)

    # Ensure unified hover behavior across all subplots
    fig.update_layout(
        template="plotly_dark",
        hovermode="x unified",  # Ensures hover across all subplots
        font=dict(family="Courier New, monospace", size=12, color="white"),
        hoversubplots="axis",
        dragmode="pan",
    )

    fig.update_traces(xaxis=f"x{rows}")

    # Ensure spikelines and hover are correctly applied across all subplots
    fig.update_xaxes(
        showspikes=True,  # Enable spike lines on the X axis
        spikemode="across",  # Spikes across the entire chart
        spikethickness=1,  # Thickness of spike lines
        spikecolor="white",  # Color of spike lines
        spikesnap="cursor",  # Align spikes with cursor position
        showline=True,  # Show axis lines
        showgrid=True,  # Show grid lines
        matches="x",  # Synchronize X-axes across subplots
        rangeslider=dict(visible=False),  # Disable the range slider
    )

    fig.update_yaxes(
        showspikes=True,  # Enable spike lines on the Y axis
        spikemode="across",  # Spikes across the entire chart
        spikethickness=1,  # Thickness of spike lines
        spikecolor="white",  # Color of spike lines
        spikesnap="cursor",  # Align spikes with cursor position
        showline=True,  # Show axis lines
        showgrid=True,  # Show grid lines
    )

    return fig


def store_plot_file(
    fig, filename: str, directory: str, auto_open: bool = False
) -> None:
    """
    Generate a plot html file from pre populated fig plotly object
    :param fig: Plotly Figure to plot
    :param filename: Name to store the file as
    :param directory: Directory to store the file in
    :param auto_open: Automatically open files saved
    :return: None
    """
    path = Path(directory)
    path.mkdir(parents=True, exist_ok=True)

    _filename = path.joinpath(filename)
    config = {"scrollZoom": True}
    plot(fig, filename=str(_filename), auto_open=auto_open, config=config)
    logger.info(f"Stored plot as {_filename}")


def generate_figures_from_dataframes(dataframes: List, title, plot_config):
    """
    Generate a list of candlestick chart figures from a list of DataFrames using the same title.

    Parameters:
        dataframes (list of pd.DataFrame): List of DataFrames, each containing 'Open', 'High', 'Low', and 'Close' columns.
        title (str): The title for all the charts.
        plot_config (dict): Configuration dictionary for customizing the plots.

    Returns:
        list of go.Figure: List of Plotly figure objects.
    """

    figures = []

    # Using tqdm to display a progress bar
    for df in tqdm(dataframes, desc="Generating Figures"):
        fig = generate_candlestick_graph(title=title, data=df, plot_config=plot_config)
        figures.append(fig.to_dict())

    return figures
