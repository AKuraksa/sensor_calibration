# Názvy vstupních souborů (zadejte seznam názvů bez přípony)
# files = ["nazev", "nazev", "nazev"]
files = ["co_15", "klarka"]
# Body měření
show_points = True

import pandas as pd
import numpy as np
from scipy.interpolate import interp1d
import plotly.graph_objects as go


def load_and_interpolate(file_path, reference_date=None):
    try:
        # Načtení CSV souboru se správným oddělovačem
        data = pd.read_csv(file_path, delimiter=',')

        # Zobrazení názvů sloupců pro ladění
        print(f"Columns in {file_path}: {data.columns}")

        # Kontrola existence sloupců 'date' a 'temp'
        if 'date' not in data.columns or 'temp' not in data.columns:
            raise KeyError("'date' or 'temp' column wasnt found")

        # Zpracování hodnot 'N/D' a čárky jako desetinné tečky, pokud jsou hodnoty řetězce
        if data['temp'].dtype == 'object':
            data['temp'] = data['temp'].replace('N/D', np.nan).str.replace(',', '.').astype(float)
        else:
            data['temp'] = data['temp'].replace('N/D', np.nan).astype(float)

        # Extrakce sloupců 'date' a 'time'
        date = data['date'].iloc[0]  # Předpoklad, že všechny řádky mají stejné datum
        time_str = data['time']

        # Porovnání referenčního data s datem aktuálního souboru, pokud je poskytováno
        if reference_date and date != reference_date:
            proceed = input(f"Varování: Zjištěna nesrovnalost data. Očekáváno {reference_date}, nalezeno {date}. Pokračovat? (ano/a/yes/y): ")
            if proceed.lower() not in ['ano', 'a', 'yes', 'y']:
                print("Skript ukončen.")
                return None, None, None, None, None

        # Konverze času na pandas datetime bez data
        time_seconds = pd.to_datetime(time_str, format='%H:%M:%S')

        # Debug: Výpis skutečných časových údajů
        # print("Actual time values:", time_seconds.tolist())

        # Extrakce teplotních hodnot
        temperature = data['temp']

        # Interpolační funkce
        interpolation_function = interp1d(time_seconds.astype(np.int64) / 10**9, temperature, kind='linear', fill_value="extrapolate")

        return time_seconds.dt.time, temperature, interpolation_function, date, data

    except Exception as e:
        print(f"Chyba při načítání a interpolaci dat ze souboru {file_path}: {e}")
        return None, None, None, None, None

def plot_data(files, show_points=False):
    reference_date = None
    fig = go.Figure()

    for file in files:
        file_path = f"./data_parsed/{file}.csv"
        time_seconds, temperature, interpolation_function, date, data = load_and_interpolate(file_path, reference_date)
        
        if time_seconds is None:
            continue
        
        # Nastavení referenčního data, pokud se jedná o první soubor
        if reference_date is None:
            reference_date = date
        
        # Generování plného rozsahu času v datetime pro graf (bez data)
        min_time, max_time = pd.to_datetime(time_seconds, format='%H:%M:%S').min(), pd.to_datetime(time_seconds, format='%H:%M:%S').max()
        full_time_range = pd.date_range(start=f"2000-01-01 {min_time}", end=f"2000-01-01 {max_time}", freq='s').time

        # Seřazení full_time_range
        full_time_range = sorted(full_time_range)

        # Pokračování s interpolací
        interpolated_temp = interpolation_function(pd.to_datetime(full_time_range, format='%H:%M:%S').astype(np.int64) / 10**9)
        
        # Extrakce názvu souboru bez cesty a přípony
        file_name = file
        
        # Kontrola, zda se jedná o soubor "klarka" a přidání tolerančního rozmezí
        if 'klarka' in file.lower():
            fig.add_trace(go.Scatter(
                x=full_time_range, y=interpolated_temp, mode='lines',
                name=f'Klárka ({date})', line=dict(color='purple')
            ))
            fig.add_trace(go.Scatter(
                x=full_time_range, y=interpolated_temp + 0.5, mode='lines',
                name=f'+0.5°C Klárka ({date})', line=dict(dash='dash', color='purple')
            ))
            fig.add_trace(go.Scatter(
                x=full_time_range, y=interpolated_temp - 0.5, mode='lines',
                name=f'-0.5°C Klárka ({date})', line=dict(dash='dash', color='purple')
            ))

            # Přidání bodů pro skutečná měření, pokud je show_points True
            if show_points:
                fig.add_trace(go.Scatter(
                    x=time_seconds, y=temperature, mode='markers', name=f'Měření ({date})',
                    marker=dict(color='red', size=8, symbol='circle')
                ))

            # Přidání grafové stopy pro DoorOpen, pokud sloupec existuje
            if 'door_open' in data.columns:
                door_open = data["door_open"].astype(int)
            else:
                door_open = -1 * np.ones(len(time_seconds))
            fig.add_trace(go.Scatter(
                x=time_seconds, y=door_open, mode='lines',
                name='DoorOpen', line=dict(color='red', dash='dot')
            ))
        else:
            # Vykreslení teplotních dat
            fig.add_trace(go.Scatter(
                x=full_time_range, y=interpolated_temp, mode='lines', name=f'{file_name} ({date})'
            ))
            
            # Přidání bodů pro skutečná měření, pokud je show_points True
            if show_points:
                fig.add_trace(go.Scatter(
                    x=time_seconds, y=temperature, mode='markers', name=f'Měření ({date})',
                    marker=dict(color='red', size=8, symbol='circle')
                ))
    
    # Přidání textu o průměrných intervalech do layoutu grafu
    fig.update_layout(
        title='Teplotní data',
        xaxis_title='Čas',
        yaxis_title='Teplota (°C)',
        hovermode='x unified',
        xaxis=dict(tickformat='%H:%M:%S'),
    )
    if __name__ == "__main__":
        fig.show()
    else:
        return fig

def main():
    # Hlavní logika pro testování
    plot_data(files, show_points)

if __name__ == "__main__":
    main()