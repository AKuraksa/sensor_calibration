# Cesty k souborům
sensor_1 = "klarka"
sensor_2 = "co_15"

# Celkový časový rozsah (volitelné)
# global_time_range = ("17:50:00", "19:15:00")
global_time_range = ()

# Intervaly pro zvýraznění (volitelné)
# highlight_intervals = [ ("18:00:00", "18:05:00"), ("18:15:00", "18:20:00"), ("18:40:00", "19:00:00") ]
# ("16:50:00", "17:19:00"), ("17:30:00", "17:49:00")
highlight_intervals = []

import pandas as pd
import numpy as np
import plotly.graph_objects as go

# Boolean přepínač
merge_highlight_intervals = True

def load_and_process(file_path):
    try:
        data = pd.read_csv(file_path, delimiter=',')
        if data['temp'].dtype == 'object':
            data['temp'] = data['temp'].replace('N/D', np.nan).str.replace(',', '.').astype(float)
        else:
            data['temp'] = data['temp'].replace('N/D', np.nan).astype(float)
        return data[['date', 'time', 'temp']]
    except Exception as e:
        print(f"Chyba při načítání souboru {file_path}: {e}")
        return None

def average_in_time_blocks(data, freq='5min'):
    try:
        data['time'] = pd.to_datetime(data['time'], format='%H:%M:%S').dt.time
        data['datetime'] = pd.to_datetime(data['time'].astype(str), format='%H:%M:%S')
        data = data.set_index('datetime')
        averaged = data.resample(freq).mean(numeric_only=True)
        averaged['time'] = averaged.index.time
        return averaged.dropna().reset_index()
    except Exception as e:
        print(f"Chyba při zpracování časových bloků: {e}")
        return None

def plot_calibrated_data(sensor_1, sensor_2, global_time_range=None, highlight_intervals=None):
    try:
        # Load data
        data_1 = load_and_process(sensor_1)
        data_2 = load_and_process(sensor_2)

        if data_1 is None or data_2 is None:
            print("Chyba: Nebylo možné načíst nebo zpracovat data.")
            return

        # Checking the dates to ensure consistency
        date_1 = data_1['date'].iloc[0]
        date_2 = data_2['date'].iloc[0]
        if date_1 != date_2:
            proceed = input(f"Varování: Zjištěna nesrovnalost data. Očekáváno {date_1}, nalezeno {date_2}. Pokračovat? (ano/a/yes/y): ")
            if proceed.lower() not in ['ano', 'a', 'yes', 'y']:
                print("Skript ukončen.")
                return

        # Debugging: Print first few entries for sensor 1 and sensor 2
        #print("Sensor 1 sample data:", data_1.head())
        #print("Sensor 2 sample data:", data_2.head())

        # Convert times to pandas datetime objects for easier processing
        data_1['time'] = pd.to_datetime(data_1['time'], format='%H:%M:%S', errors='coerce').dt.time
        data_2['time'] = pd.to_datetime(data_2['time'], format='%H:%M:%S', errors='coerce').dt.time

        # Check for NaT values and remove rows where time is invalid
        if data_1['time'].isna().any() or data_2['time'].isna().any():
            print("Warning: Some time values are invalid (NaT). These will be removed.")
            data_1 = data_1.dropna(subset=['time'])
            data_2 = data_2.dropna(subset=['time'])

        # Debugging: Print after cleaning the data
        #print("Sensor 1 cleaned data:", data_1.head())
        #print("Sensor 2 cleaned data:", data_2.head())

        if global_time_range:
            start_time, end_time = [pd.to_datetime(t, format='%H:%M:%S').time() for t in global_time_range]
            data_1 = data_1[(data_1['time'] >= start_time) & (data_1['time'] <= end_time)]
            data_2 = data_2[(data_2['time'] >= start_time) & (data_2['time'] <= end_time)]

        # Proceed with averaging and merging data
        data_1_avg = average_in_time_blocks(data_1)
        data_2_avg = average_in_time_blocks(data_2)

        # Merge the two dataframes
        merged = pd.merge_asof(data_1_avg, data_2_avg, on='datetime', suffixes=('_1', '_2'))

        merged['time'] = merged['datetime'].dt.time

        # Create the plot
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=merged['temp_1'],
            y=merged['temp_2'],
            mode='markers+lines',
            name='Kalibrační data',
            marker=dict(size=8, color='blue')
        ))

        # Optional: Add highlight intervals
        if highlight_intervals:
            for start, end in highlight_intervals:
                start_time, end_time = [pd.to_datetime(t, format='%H:%M:%S').time() for t in (start, end)]
                interval_data = merged[(merged['time'] >= start_time) & (merged['time'] <= end_time)]
                for _, row in interval_data.iterrows():
                    fig.add_trace(go.Scatter(
                        x=[row['temp_1']],
                        y=[row['temp_2']],
                        mode='markers',
                        name=f'Ustálený bod ({start} - {end})',
                        marker=dict(size=12, color='red', symbol='diamond')
                    ))

        # Add the x = y line
        min_temp = min(merged['temp_1'].min(), merged['temp_2'].min())
        max_temp = max(merged['temp_1'].max(), merged['temp_2'].max())
        fig.add_trace(go.Scatter(
            x=[min_temp, max_temp],
            y=[min_temp, max_temp],
            mode='lines',
            name='x = y',
            line=dict(dash='dash', color='red')
        ))

        fig.update_layout(
            title='Kalibrace teplotních senzorů',
            xaxis_title='Teplota senzoru 1 (°C)',
            yaxis_title='Teplota senzoru 2 (°C)',
            xaxis=dict(scaleanchor="y", scaleratio=1),
            yaxis=dict(scaleanchor="x", scaleratio=1),
            hovermode='closest'
        )

        return fig
    except Exception as e:
        print(f"Chyba při vytváření grafu: {e}")
        return None

def main():
    fig = plot_calibrated_data(f"./data_parsed/{sensor_1}.csv", f"./data_parsed/{sensor_2}.csv", global_time_range, highlight_intervals)
    fig.show()

if __name__ == '__main__':
    main()