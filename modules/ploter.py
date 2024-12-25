import pandas as pd
import numpy as np
from scipy.interpolate import interp1d
import plotly.graph_objects as go
import os

def load_file(file_path):
    """
    Load and process a CSV file.

    Parameters:
        file_path (str): Path to the CSV file.

    Returns:
        pd.DataFrame: Processed data.
    """
    data = pd.read_csv(file_path, delimiter=',')
    if 'date' not in data.columns or 'temp' not in data.columns or 'time' not in data.columns:
        raise KeyError(f"'date', 'temp or 'time' {file_path} not exist.")

    # Handle missing data and decimal separators
    if data['temp'].dtype == object:  # Check if 'temp' contains strings
        data['temp'] = data['temp'].replace('N/D', np.nan).str.replace(',', '.').astype(float)
    else:
        data['temp'] = data['temp'].replace('N/D', np.nan)  # No .str.replace() needed

    # Convert 'time' to datetime
    data['time'] = pd.to_datetime(data['time'], format='%H:%M:%S')

    # Debug: Print first few rows of the processed data
    # print(f"Processed data from {file_path}:\n{data.head()}")
    return data

def interpolate_data(data):
    """
    Create an interpolation function for temperature data.

    Parameters:
        data (pd.DataFrame): Data with 'time' and 'temp' columns.

    Returns:
        interp1d: Interpolation function.
    """
    time_seconds = data['time'].astype(np.int64) // 10**9
    temp = data['temp']

    # Debug: Print interpolation input ranges
    # print(f"Interpolation input time range: {time_seconds.min()} - {time_seconds.max()}")
    return interp1d(
        time_seconds, temp, kind='linear', fill_value="extrapolate"
    )

def calculate_global_min_time(files):
    """
    Calculate the earliest time across all files.

    Parameters:
        files (list): List of file paths.

    Returns:
        pd.Timestamp: Earliest time found in the files.
    """
    min_time = None
    for file_path in files:
        data = pd.read_csv(file_path, delimiter=',')
        file_min_time = pd.to_datetime(data['time'], format='%H:%M:%S').min()
        if min_time is None or file_min_time < min_time:
            min_time = file_min_time

    # Debug: Print global minimum time
    # print(f"Global minimum time: {min_time}")
    return min_time

def plot_figure(files, ref_file=None, show_points=False):
    """
    Plot temperature data with optional reference file.

    Parameters:
        files (list): List of file names without extensions.
        ref_file (str): Reference file name (without extension).
        show_points (bool): Whether to display actual data points on the graph.

    Returns:
        None
    """
    file_paths = validate_files(files)
    fig = go.Figure()
    global_min_time = calculate_global_min_time(file_paths)

    for file_path in file_paths:
        try:
            # Load and process file
            data = load_file(file_path)
            interpolation_function = interpolate_data(data)
            time_seconds = data['time']
            temperature = data['temp']
            full_time_range = pd.date_range(start=global_min_time, end=time_seconds.max(), freq='s')

            # Debug: Check time and temperature ranges
            #print(f"File: {file_path}")
            #print(f"Time range: {time_seconds.min()} - {time_seconds.max()}")
            #print(f"Temperature stats: {temperature.describe()}")

            # Interpolate temperature over the full time range
            interpolated_temp = interpolation_function(
                full_time_range.astype(np.int64) // 10**9
            )

            # Extract file name without extension
            file_name = os.path.basename(file_path).replace('.csv', '')

            if ref_file and ref_file in file_path:
                # Plot reference file with tolerance bands
                fig.add_trace(go.Scatter(x=full_time_range, y=interpolated_temp, mode='lines', name=f'{file_name}' , line=dict(color='purple')))
                fig.add_trace(go.Scatter(
                    x=full_time_range, y=interpolated_temp + 0.5, mode='lines',
                    name=f'+0.5°C {file_name}', line=dict(dash='dash', color='purple')
                ))
                fig.add_trace(go.Scatter(
                    x=full_time_range, y=interpolated_temp - 0.5, mode='lines',
                    name=f'-0.5°C {file_name}', line=dict(dash='dash', color='purple')
                ))
            else:
                # Plot regular file data
                fig.add_trace(go.Scatter(x=full_time_range, y=interpolated_temp, mode='lines', name=f'{file_name}'))

            if show_points:
                # Plot actual data points
                fig.add_trace(go.Scatter(
                    x=time_seconds, y=temperature, mode='markers', name=f'Měření {file_name}',
                    marker=dict(color='red', size=8, symbol='circle')
                ))

            try:
                data = pd.read_csv(file_path, delimiter=',')  # Reload for door_open
                if 'door_open' in data.columns:
                    door_open = data['door_open'].astype(int)
                    fig.add_trace(go.Scatter(
                        x=time_seconds, 
                        y=door_open, 
                        mode='lines', 
                        name=f'Stav dveří ({file_name})', 
                        line=dict(color='red', dash='dot')
                    ))
            except Exception as e:
                print(f"Error: door_open {file_name}: {e}")

        except Exception as e:
            print(f"Error processing file {file_path}: {e}")

    # Configure the graph layout
    fig.update_layout(
        title='Temp data',
        xaxis_title='Time',
        yaxis_title='Temperature (°C)',
        hovermode='x unified',
        xaxis=dict(tickformat='%H:%M:%S'),
    )
    return fig

def main():
    """
    Main function to execute the script.
    """
    files = input("Enter file names (comma-separated, without extensions): ").split(',')
    files = [file.strip() for file in files]
    ref_file = input("Enter reference file (without extension): ").strip()
    show_points = input("Show points on the graph? (yes/y to enable, default: no): ").lower() in ['yes', 'y']

    if ref_file and ref_file not in files:
        print(f"Error: Reference file '{ref_file}' is not in the list of provided files: {', '.join(files)}.")
        proceed = input("Do you want to continue without a reference file? (yes/y to continue, default: no): ").strip().lower()
        if proceed not in ['yes', 'y']:
            print("Exiting program.")
            return
        else:
            ref_file = None 

    fig = plot_figure(files, ref_file=ref_file, show_points=show_points)
    fig.show()

if __name__ == "__main__":
    from tools import validate_files
    main()
else:
    from modules.tools import validate_files
