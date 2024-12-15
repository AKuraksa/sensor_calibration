# Cesty k souborům
sensor_1 = "co-15"
sensor_2 = "klarka"

# Celkový časový rozsah (volitelné)
# global_time_range = ("17:50:00", "19:15:00")
global_time_range = ()

# Intervaly pro zvýraznění (volitelné)
# highlight_intervals = [ ("18:00:00", "18:05:00"), ("18:15:00", "18:20:00"), ("18:40:00", "19:00:00") ]
highlight_intervals = []

"""
Tento skript je určen k načítání a zpracování dat ze souborů CSV, jejich průměrování po časových blocích a vytvoření scatter plotu pro kalibraci teplotních senzorů pomocí knihovny Plotly.

Funkce:
- Načítá data ze složky `data_parsed` podle zadaného názvu souboru.
- Zpracovává data:
  - Načítá CSV soubor, převádí data do správného formátu a vrací DataFrame se sloupci 'time', 'temp', a 'date'.
  - Rozděluje data do časových bloků podle zadané frekvence a vrací průměry.
  - Sloučí data ze dvou senzorů na základě blízkého času.
- Vytváří scatter plot:
  - Hodnoty ze senzoru 1 jsou na ose x a hodnoty ze senzoru 2 na ose y.
  - Zvýrazňuje body v zadaných intervalech, pokud jsou definovány.
  - Přidává osu x = y jako referenční linii.
  - Nastavuje graf tak, aby rozsah osy x byl stejný jako rozsah osy y.

Použití:
- Upravte proměnné `sensor_1_file` a `sensor_2_file`, aby obsahovaly názvy vašich souborů bez přípony.
- Pokud je to potřebné, upravte proměnnou `global_time_range` pro omezení celkového časového rozsahu.
- Pokud je to potřebné, upravte seznam `highlight_intervals` pro zvýraznění bodů v zadaných intervalech.
- Spusťte skript pro načtení, zpracování a průměrování dat, a následné vytvoření scatter plotu pro kalibraci teplotních senzorů.

Autor:
Microsoft Copilot
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go

def load_and_process(file_path):
    """
    Načte CSV soubor, převede data do správného formátu a vrátí DataFrame se sloupci 'time', 'temp', a 'date'.
    """
    try:
        data = pd.read_csv(file_path, delimiter=',')

        # Zpracování teploty: nahrazení čárky tečkou a konverze na float
        if data['temp'].dtype == 'object':
            data['temp'] = data['temp'].replace('N/D', np.nan).str.replace(',', '.').astype(float)
        else:
            data['temp'] = data['temp'].replace('N/D', np.nan).astype(float)

        # Vrátí pouze potřebné sloupce
        return data[['date', 'time', 'temp']]
    except Exception as e:
        print(f"Chyba při načítání souboru {file_path}: {e}")
        return None

def average_in_time_blocks(data, freq='5min'):
    """
    Rozdělí data do časových bloků podle zadané frekvence a vrátí průměry.
    """
    try:
        # Převod času na datetime a nastavení jako index
        data['time'] = pd.to_datetime(data['time'], format='%H:%M:%S').dt.time
        data['datetime'] = pd.to_datetime(data['time'].astype(str), format='%H:%M:%S')
        data = data.set_index('datetime')

        # Resampling podle zadané frekvence
        averaged = data.resample(freq).mean(numeric_only=True)
        # Filtrujeme pouze řádky, kde je teplota k dispozici
        averaged['time'] = averaged.index.time
        return averaged.dropna().reset_index()
    except Exception as e:
        print(f"Chyba při zpracování časových bloků: {e}")
        return None

def plot_calibrated_data(sensor_1, sensor_2, global_time_range=None, highlight_intervals=None):
    """
    Vytvoří scatter plot, kde hodnoty ze senzoru 1 jsou na ose x a ze senzoru 2 na ose y.
    """
    try:
        # Načtení a zpracování dat
        data_1 = load_and_process(sensor_1)
        data_2 = load_and_process(sensor_2)

        if data_1 is None or data_2 is None:
            print("Chyba: Nebylo možné načíst nebo zpracovat data.")
            return

        # Kontrola, zda oba soubory mají stejný datum
        date_1 = data_1['date'].iloc[0]
        date_2 = data_2['date'].iloc[0]
        if date_1 != date_2:
            proceed = input(f"Varování: Zjištěna nesrovnalost data. Očekáváno {date_1}, nalezeno {date_2}. Pokračovat? (ano/a/yes/y): ")
            if proceed.lower() not in ['ano', 'a', 'yes', 'y']:
                print("Skript ukončen.")
                return

        # Převod 'time' sloupce na datetime.time objekty
        data_1['time'] = pd.to_datetime(data_1['time'], format='%H:%M:%S').dt.time
        data_2['time'] = pd.to_datetime(data_2['time'], format='%H:%M:%S').dt.time

        print("Processed time columns for both datasets.")

        # Omezení na celkový časový rozsah, pokud je definován
        if global_time_range:
            start_time, end_time = [pd.to_datetime(t, format='%H:%M:%S').time() for t in global_time_range]
            data_1 = data_1[(data_1['time'] >= start_time) & (data_1['time'] <= end_time)]
            data_2 = data_2[(data_2['time'] >= start_time) & (data_2['time'] <= end_time)]

        print("Applied global time range filter.")

        # Průměrování po 5minutových blocích
        data_1_avg = average_in_time_blocks(data_1)
        data_2_avg = average_in_time_blocks(data_2)

        print("Calculated average in time blocks.")

        # Sloučení dat na základě blízkého času
        merged = pd.merge_asof(data_1_avg, data_2_avg, on='datetime', suffixes=('_1', '_2'))

        print("Merged datasets.")
        
        # Add back the 'time' column for use in plotting
        merged['time'] = merged['datetime'].dt.time

        # Vytvoření scatter plotu
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=merged['temp_1'],
            y=merged['temp_2'],
            mode='markers+lines',
            name='Kalibrační data',
            marker=dict(size=8, color='blue')
        ))

        # Zvýraznění bodů v zadaných intervalech, pokud jsou definovány
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

        print("Added highlighted intervals.")

        # Přidání osy x = y jako referenční linie
        min_temp = min(merged['temp_1'].min(), merged['temp_2'].min())
        max_temp = max(merged['temp_1'].max(), merged['temp_2'].max())
        fig.add_trace(go.Scatter(
            x=[min_temp, max_temp],
            y=[min_temp, max_temp],
            mode='lines',
            name='x = y',
            line=dict(dash='dash', color='red')
        ))

        # Nastavení grafu
        fig.update_layout(
            title='Kalibrace teplotních senzorů',
            xaxis_title='Teplota senzoru 1 (°C)',
            yaxis_title='Teplota senzoru 2 (°C)',
            xaxis=dict(scaleanchor="y", scaleratio=1),
            yaxis=dict(scaleanchor="x", scaleratio=1),
            hovermode='closest'
        )

        print("Plot ready to be shown.")

        fig.show()
    except Exception as e:
        print(f"Chyba při vytváření grafu: {e}")

# Spuštění skriptu
plot_calibrated_data(f"./data_parsed/{sensor_1}.csv", f"./data_parsed/{sensor_2}.csv", global_time_range, highlight_intervals)