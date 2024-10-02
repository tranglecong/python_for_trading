
# Python For Trading

This repository contains an implementation of a trading strategy using multiple technical indicators and pattern detection. The strategy analyzes historical price data to generate signals for entering and exiting trades based on specific conditions defined through various technical indicators. Additionally, the implementation includes visualizations using Plotly for candlestick charts.

## Project Overview

The project includes a script that:

1. **Loads Historical Data**: Uses a pre-saved dataset (e.g., `BTC_USDT_USDT-1h-futures.feather`) to analyze trading data.
2. **Applies Technical Indicators**: Populates the DataFrame with multiple technical indicators.
3. **Generates Trading Signals**: Creates buy (`enter_long`) and sell (`enter_short`) signals based on a combination of technical indicators.
4. **Creates Visualizations**: Generates and saves a candlestick chart using Plotly.

## Dependencies

To run the project, install the required Python libraries:

```bash
pip install -r requirements.txt
```

If you need to install TA-Lib, follow the [TA-Lib installation guide](https://mrjbq7.github.io/ta-lib/install.html) for your specific platform.

## Running the Sample Script

To run the script, use the following command:

```bash
python3 sample.py
```

The script will:

1. Load historical data from a specified file.
2. Apply technical indicators and generate trading signals.
3. Create a candlestick chart with the results.
4. Save the generated chart as an HTML file in the `./plot` directory.

## File Structure

- **`indicators/`**: Custom indicator files for analysis.
- **`plotting/`**: Utilities for plotting and visualizing the results.
- **`utils/`**: Helper functions for logging and loading data.
- **`data/`**: Folder containing sample datasets (ensure the correct file path in the script).
- **`plot/`**: Folder containing generated html candlestick chart.

## Example Visualization

Below is an example of a generated candlestick chart with various indicators overlayed.

![Example Chart](https://github.com/tranglecong/python_for_trading/blob/main/.docs/example_chart.png?raw=true)

## Usage Notes

- Make sure to adjust the file paths and date ranges as needed based on your data and analysis requirements.
- The sample dataset should be in a format compatible with Pandas, e.g., Feather, CSV.

## Contributions

Feel free to fork this repository, submit issues, and make pull requests if you have suggestions or improvements for the strategy or visualizations.
