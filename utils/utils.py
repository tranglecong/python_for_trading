import time

import pandas as pd


def load_dataframe(file_path: str) -> pd.DataFrame:
    """
    Load a DataFrame from a CSV or Feather file.

    Parameters:
    - file_path: str, path to the CSV or Feather file

    Returns:
    - pd.DataFrame: Loaded DataFrame
    """
    if file_path.endswith(".csv"):
        return pd.read_csv(file_path)
    elif file_path.endswith(".feather"):
        return pd.read_feather(file_path)
    else:
        raise ValueError(
            "Unsupported file format. Please provide a .csv or .feather file."
        )


def dataframe_date_to_date(
    df: pd.DataFrame,
    start_date: str,
    end_date: str,
    date_column: str = "date",
    prepare: int = 0,
) -> pd.DataFrame:
    """
    Get a range of rows from a DataFrame based on a date range, and reset the index.
    Optionally, include additional rows before the start date.

    Parameters:
    - df (pd.DataFrame): The DataFrame that contains the data.
    - start_date (str): The start date in 'YYYY-MM-DD' format.
    - end_date (str): The end date in 'YYYY-MM-DD' format.
    - date_column (str): The name of the date column in the DataFrame (default is 'date').
    - prepare (int): Number of rows to include before the start date (default is 0).

    Returns:
    - pd.DataFrame: A DataFrame filtered by the date range, including the additional rows if specified,
      with the index reset.
    """
    # Ensure the date column is in datetime format
    df[date_column] = pd.to_datetime(df[date_column])

    # Sort the DataFrame by the date column to ensure proper ordering
    df = df.sort_values(by=date_column)

    # Find the index of the first row that matches the start date
    start_index = df[df[date_column] >= start_date].index[0]

    # Calculate the adjusted start index, ensuring it's non-negative
    adjusted_start_index = max(0, start_index - prepare)

    # Filter the DataFrame by the adjusted start index and end date
    mask = (df[date_column] >= df.iloc[adjusted_start_index][date_column]) & (
        df[date_column] <= end_date
    )
    filtered_df = df.loc[mask]

    # Reset the index
    filtered_df.reset_index(drop=True, inplace=True)

    return filtered_df


def generate_sub_dataframes(dataframe: pd.DataFrame, length: int):
    """
    Generate a list of sub-dataframes from the original dataframe.
    Each sub-dataframe has the specified length and moves one index forward.

    Parameters:
        dataframe (pd.DataFrame): The original dataframe.
        length (int): The length of each sub-dataframe.

    Returns:
        list: A list of sub-dataframes.
    """
    if length > len(dataframe):
        raise ValueError(
            "Length of sub-dataframes cannot be greater than the length of the original dataframe."
        )

    sub_dataframes = []
    for start in range(len(dataframe) - length + 1):
        sub_df = dataframe.iloc[start : start + length]
        sub_dataframes.append(sub_df)

    return sub_dataframes


def measure_time(func, *args, **kwargs):
    """
    Measure the execution time of a function.

    Parameters:
        func (callable): The function to measure.
        *args: Positional arguments to pass to the function.
        **kwargs: Keyword arguments to pass to the function.

    Returns:
        result: The result of the function call.
        execution_time: Time taken to execute the function.
    """
    start_time = time.time()
    result = func(*args, **kwargs)
    end_time = time.time()
    execution_time = end_time - start_time
    return result, execution_time
