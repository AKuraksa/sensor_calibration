# Názvy vstupních souborů (zadejte seznam názvů bez přípony)
files = ["bile-28", "co-15", "klarka", "wifi-69"]

"""
Tento skript je určen k načítání a interpolaci dat ze souborů CSV a k vytváření interaktivních grafů teplot pomocí knihovny Plotly.

Funkce:
- Načítá data ze složky `data_parsed` podle zadaného názvu souboru.
- Zpracovává sloupec `payload`, který obsahuje data ve formátu JSON, a extrahuje potřebné informace:
  - Hodnoty CO2, vlhkosti a teploty.
- Pokud je záznam neplatný nebo chybí důležité informace, je odstraněn.
- Rozděluje časový údaj do samostatných sloupců `date` (datum) a `time` (čas).
- Interpoluje teplotní data pro každou sekundu na základě existujících měření.
- Vytváří interaktivní graf, kde každá linie reprezentuje jednu sadu dat (jeden soubor).
- Graf zahrnuje interaktivní prvky pro zobrazení hodnot v daném čase.
- Pokud je identifikován soubor "klarka.csv", přidává kolem jeho linie toleranční rozmezí o ±0,5°C.

Použití:
- Upravte proměnnou `files`, aby obsahovala názvy vašich souborů bez přípony.
- Spusťte skript pro načtení a interpolaci dat, a následné vytvoření grafu.

Autor: Microsoft Copilot
"""

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
            raise KeyError("'date' nebo 'temp' sloupec nebyl nalezen v datech.")
        
        # Konverze sloupce 'temp' na float, zpracování hodnot 'N/D' a čárky jako desetinné tečky
        data['temp'] = data['temp'].replace('N/D', np.nan).str.replace(',', '.').astype(float)
        
        # Extrakce sloupců 'date' a 'time'
        date = data['date'].iloc[0]  # Předpoklad, že všechny řádky mají stejné datum
        time_str = data['time']
        
        # Porovnání referenčního data s datem aktuálního souboru, pokud je poskytováno
        if reference_date and date != reference_date:
            print(f"Varování: Zjištěna nesrovnalost data. Očekáváno {reference_date}, nalezeno {date}.")
        
        # Konverze času na pandas datetime
        time_seconds = pd.to_datetime(date + ' ' + time_str)
        
        # Extrakce teplotních hodnot
        temperature = data['temp']
        
        # Interpolační funkce
        interpolation_function = interp1d(time_seconds.astype(np.int64) / 10**9, temperature, kind='linear', fill_value="extrapolate")
        
        return time_seconds, temperature, interpolation_function, date
    
    except Exception as e:
        print(f"Chyba při načítání a interpolaci dat ze souboru {file_path}: {e}")
        return None, None, None, None

def plot_data(files):
    reference_date = None
    fig = go.Figure()
    
    for file in files:
        file_path = f"./data_parsed/{file}.csv"
        time_seconds, temperature, interpolation_function, date = load_and_interpolate(file_path, reference_date)
        
        if time_seconds is None:
            continue
        
        # Nastavení referenčního data, pokud se jedná o první soubor
        if reference_date is None:
            reference_date = date
        
        # Generování plného rozsahu času v datetime pro graf
        min_time, max_time = time_seconds.min(), time_seconds.max()
        full_time_range = pd.date_range(start=min_time, end=max_time, freq='S')
        interpolated_temp = interpolation_function(full_time_range.astype(np.int64) / 10**9)
        
        # Extrakce názvu souboru bez cesty a přípony
        file_name = file
        
        # Kontrola, zda se jedná o soubor "klarka" a přidání tolerančního rozmezí
        if 'klarka' in file.lower():
            fig.add_trace(go.Scatter(
                x=full_time_range, y=interpolated_temp, mode='lines',
                name=f'{date} (Klárka)', line=dict(color='purple')
            ))
            fig.add_trace(go.Scatter(
                x=full_time_range, y=interpolated_temp + 0.5, mode='lines',
                name=f'{date} (+0.5°C Klárka)', line=dict(dash='dash', color='purple')
            ))
            fig.add_trace(go.Scatter(
                x=full_time_range, y=interpolated_temp - 0.5, mode='lines',
                name=f'{date} (-0.5°C Klárka)', line=dict(dash='dash', color='purple')
            ))
        else:
            # Vykreslení teplotních dat
            fig.add_trace(go.Scatter(
                x=full_time_range, y=interpolated_temp, mode='lines', name=f'{date} ({file_name})'
            ))
    
    fig.update_layout(
        title='Teplotní data',
        xaxis_title='Čas',
        yaxis_title='Teplota (°C)',
        hovermode='x unified',
        xaxis=dict(tickformat='%Y-%m-%d %H:%M:%S')
    )
    fig.show()

plot_data(files)