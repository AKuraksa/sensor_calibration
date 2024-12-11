# Sensor Data Viewer a Analyzer

Aplikace pro zpracování a vizualizaci senzorových dat, postavená na Pythonu. Tento nástroj načítá CSV soubor obsahující měření senzorů (např. CO2, vlhkost, teplota), zpracovává data a zobrazuje je v interaktivním rozhraní. Umožňuje uživatelům vizualizovat trendy senzorů, kontrolovat konzistenci časových razítek a efektivně analyzovat data.

### Funkce

* **Podpora CSV souborů** : Zpracovává senzorová data se sloupci pro `id`, `date`, `time`, `topic`, `co2`, `humidity`, `temp`.
* **Vizualizace na základě času** : Zobrazuje data v průběhu času s možností přizpůsobení grafů (CO2, vlhkost, teplota).
* **Kontrola konzistence dat** : Automaticky kontroluje shodnost dat mezi více soubory a vydává varování v případě nesouladu dat.
* **Interaktivní navigace** : Umožňuje uživatelům procházet data a zobrazit podrobné statistiky, jako je průměrné hodnoty měření senzorů.
* **Uživatelsky přívětivé rozhraní** : Tmavé téma, responzivní rozhraní s intuitivní navigací.
* **Exportování dat** : Možnost exportu filtrovaných nebo analyzovaných dat do nového CSV souboru.

## Instalace

1. **Naklonujte repozitář** :

```
git clone https://github.com/AKuraksa/sensor_calibration.git
cd sensor_calibration
```

2. **Nastavení virtuálního prostředí** (volitelné, ale doporučené):

```
python -m venv venv
Na Windows: venv\Scripts\activate   #Na Linux: source venv/bin/activate
```

3. **Instalace požadovaných balíčků** :

```
pip install -r requirements.txt
```

## Popis programů

### parser.py

Tento skript slouží k vyčištění a zpracování surových dat ze souboru CSV.

### ploter.py

Tento skript je určen k načítání a interpolaci dat ze souborů CSV a k vytváření interaktivních grafů teplot pomocí knihovny Plotly.
