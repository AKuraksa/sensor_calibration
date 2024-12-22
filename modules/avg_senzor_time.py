import pandas as pd
import numpy as np
import os
from tools import validate_files

def load_file(file_path):
    """
    Load and process a CSV file.

    Parameters:
        file_path (str): Path to the CSV file.

    Returns:
        pd.DataFrame: DataFrame containing the data.
    """
    return pd.read_csv(file_path, delimiter=',', parse_dates=[['date', 'time']])

def calculate_average_interval(data):
    """
    Calculate the average time interval between readings.

    Parameters:
        data (pd.DataFrame): DataFrame with the data.

    Returns:
        float: Average interval in seconds.
    """
    data.sort_values(by='date_time', inplace=True)
    data['time_diff'] = data['date_time'].diff().dt.total_seconds()
    average_interval = data['time_diff'].mean()
    return average_interval

def format_interval(seconds):
    """
    Format the interval into appropriate units.

    Parameters:
        seconds (float): Interval in seconds.

    Returns:
        str: Formatted interval.
    """
    if seconds < 60:
        return f"{seconds:.2f} seconds"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.2f} minutes"
    else:
        hours = seconds / 3600
        return f"{hours:.2f} hours"

def main():
    files = input("Enter file names (comma-separated, without extensions): ").split(',')
    files = [file.strip() for file in files]

    try:
        file_paths = validate_files(files)
        for file_path in file_paths:
            try:
                data = load_file(file_path)
                average_interval = calculate_average_interval(data)
                formatted_interval = format_interval(average_interval)
                print(f"{os.path.basename(file_path)}: Average sampling interval: {formatted_interval}")
            except Exception as e:
                print(f"Error processing file {file_path}: {e}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()