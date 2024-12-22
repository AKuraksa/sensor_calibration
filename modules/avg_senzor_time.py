import pandas as pd
import numpy as np
import os

def load_file(file_path):
    """
    Load and process a CSV file.

    Parameters:
        file_path (str): Path to the CSV file.

    Returns:
        pd.DataFrame: DataFrame containing the data.
    """
    data = pd.read_csv(file_path, delimiter=',')
    data['date_time'] = pd.to_datetime(data['date'] + ' ' + data['time'])
    return data

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

def process_files(files):
    """
    Process multiple CSV files and return the average sampling intervals.

    Parameters:
        files (list): List of file names without extensions.

    Returns:
        dict: Dictionary with file names as keys and formatted intervals as values.
    """
    intervals = {}
    try:
        file_paths = validate_files(files)
        for file_path in file_paths:
            try:
                data = load_file(file_path)
                average_interval = calculate_average_interval(data)
                formatted_interval = format_interval(average_interval)
                intervals[os.path.basename(file_path)] = formatted_interval
            except Exception as e:
                print(f"Error processing file {file_path}: {e}")
    except Exception as e:
        print(f"Error: {e}")
    return intervals

def main():
    files = input("Enter file names (comma-separated, without extensions): ").split(',')
    files = [file.strip() for file in files]
    intervals = process_files(files)
    for file, interval in intervals.items():
        print(f"{file}: Average sampling interval: {interval}")

if __name__ == "__main__":
    from tools import validate_files
    main()
else:
    from modules.tools import validate_files
