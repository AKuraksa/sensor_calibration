import os
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression

# Načtení dat ze dvou souborů
file_x = './data_parsed/klarka.csv'  # Soubor pro osu X
file_y = './data_parsed/co_04.csv'  # Soubor pro osu Y

df_x = pd.read_csv(file_x)
df_y = pd.read_csv(file_y)

# Oprava sloupce 'temp' - převod na číselný formát
def clean_data(df):
    # Převod hodnot 'temp' na číselné typy (nevalidní hodnoty budou NaN)
    df['temp'] = pd.to_numeric(df['temp'].str.replace(',', '.'), errors='coerce')
    df['datetime'] = pd.to_datetime(df['time'], errors='coerce')  # Převod 'time' na datetime
    # Odstranění záznamů s nevalidními hodnotami
    return df.dropna(subset=['temp', 'datetime'])

df_x = clean_data(df_x)
df_y = clean_data(df_y)

# Ruční zadání časových bloků
time_blocks = [
    ("16:25:00", "16:35:00"),
    ("16:55:00", "17:15:00"),
    ("17:35:00", "17:45:00"),
    ("18:05:00", "18:15:00"),
    ("18:35:00", "18:45:00"),
    ("19:05:00", "19:15:00")
]

# Funkce pro průměrování hodnot v rámci bloků času
def process_data(df, blocks):
    averaged_data = []

    for start, end in blocks:
        start_time = pd.to_datetime(start)
        end_time = pd.to_datetime(end)
        
        # Filtrování dat v rámci časového bloku
        block_data = df[(df['datetime'] >= start_time) & (df['datetime'] < end_time)]
        
        # Výpočet průměrné teploty v bloku
        if not block_data.empty:
            avg_temp = block_data['temp'].mean()
            averaged_data.append({'time_block': f"{start}-{end}", 'avg_temp': avg_temp})

    return pd.DataFrame(averaged_data)

# Zpracování dat
processed_x = process_data(df_x, time_blocks)
processed_y = process_data(df_y, time_blocks)

# Sladění dat podle bloků času (společný průnik bloků)
merged_data = pd.merge(processed_x, processed_y, on='time_block', suffixes=('_x', '_y'))

# Lineární regrese
x = merged_data['avg_temp_x'].values.reshape(-1, 1)
y = merged_data['avg_temp_y'].values

model = LinearRegression()
model.fit(x, y)
k = model.coef_[0]  # Sklon přímky
q = model.intercept_  # Průsečík s osou y

# Predikce pro fitovací přímku
x_line = np.linspace(min(x), max(x), 100).reshape(-1, 1)
y_line = model.predict(x_line)

# Vykreslení pomocí Plotly
fig = go.Figure()

# Přidání ustálených bodů
fig.add_trace(go.Scatter(
    x=merged_data['avg_temp_x'],
    y=merged_data['avg_temp_y'],
    mode='markers',
    marker=dict(color='red', size=8),
    name='Ustálené body'
))

# Přidání lineárního fitu
fig.add_trace(go.Scatter(
    x=x_line.flatten(),
    y=y_line,
    mode='lines',
    line=dict(color='blue', dash='dash'),
    name=f'Lineární fit: y = {k:.2f}x + {q:.2f}'
))

# Přidání přímky x = y
fig.add_trace(go.Scatter(
    x=x_line.flatten(),
    y=x_line.flatten(),  # Nastavení y hodnot na stejné hodnoty jako x
    mode='lines',
    line=dict(color='green', dash='dot'),
    name='Přímka x = y'
))

# Nastavení grafu
fig.update_layout(
    title='Kalibrace teplotních senzorů',
    xaxis_title='Teplota senzoru X (°C)',
    yaxis_title='Teplota senzoru Y (°C)',
    legend=dict(x=0.02, y=0.98),
    template='plotly_white'
)

# Zobrazení grafu
fig.show()

# Výsledek
print(f"Rovnice přímky: y = {k:.2f}x + {q:.2f}")