import pandas as pd
import numpy as np
import plotly.graph_objects as go
from scipy.interpolate import interp1d
import os

# Funkce pro načtení CSV a interpolaci dat
def load_and_interpolate(csv_file):
    # Načteme CSV soubor
    df = pd.read_csv(csv_file)
    
    # Předpokládáme, že čas je v první kolonce a teplota ve druhé
    time = pd.to_datetime(df.iloc[:, 0])
    temperature = df.iloc[:, 1]
    
    # Převedeme čas na sekundy (pro jednodušší interpolaci)
    time_seconds = (time - time.min()).dt.total_seconds()

    # Interpolace na každý druhý
    interpolation_function = interp1d(time_seconds, temperature, kind='linear', fill_value="extrapolate")
    new_time = np.arange(time_seconds.min(), time_seconds.max(), 1)  # Každá sekunda
    new_temperature = interpolation_function(new_time)
    
    return new_time, new_temperature

# Funkce pro generování grafu
def plot_data(files):
    fig = go.Figure()

    for file in files:
        input_file = f"./data_raw/{file}.csv"
        time, temperature = load_and_interpolate(input_file)
        
        # Přidáme každou sadu dat jako jednu čáru na graf
        fig.add_trace(go.Scatter(x=time, y=temperature, mode='lines', name=os.path.basename(file)))
    
    # Nastavení os a názvů
    fig.update_layout(
        title='Teploty ze senzorů',
        xaxis_title='Čas (v sekundách)',
        yaxis_title='Teplota (°C)',
        showlegend=True
    )

    # Tlačítka pro interaktivitu
    fig.update_xaxes(rangeslider_visible=True)  # Přidá posuvník na osu X
    fig.update_yaxes(range=[min(temperature), max(temperature)])  # Dynamické rozmezí na ose Y

    fig.show()

# Funkce pro kontrolu a vytvoření tolerančního pásma pro "klárka"
def add_tolerance_for_klarka(files):
    for file in files:
        if 'klarka' in file.lower():
            input_file = f"./data_raw/{file}.csv"
            df = pd.read_csv(input_file)
            klarka_value = df.iloc[:, 1].mean()  # Předpokládáme, že teplota je ve druhé kolonce
            lower_bound = klarka_value - 0.5
            upper_bound = klarka_value + 0.5
            print(f"Soubor {file} obsahuje klárku. Toleranční rozmezí: {lower_bound} °C - {upper_bound}")
            # Můžeme přidat k vykreslení i tento rozsah
            fig.add_shape(
                type="rect",
                x0=0, x1=1,
                y0=lower_bound, y1=upper_bound,
                line=dict(color="RoyalBlue", width=2),
                fillcolor="LightSkyBlue", opacity=0.3
            )

# Seznam CSV souborů pro analýzu
files = ["bile-28", "co-15", "klarka", "wifi-69"]  # Nahraď názvy tvými soubory

# Přidáme toleranci pro "klárka"
add_tolerance_for_klarka(files)

# Vykreslíme data
plot_data(files)