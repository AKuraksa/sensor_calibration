## ploter.py

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
- Zobrazuje průměrný časový interval mezi měřeními pro každý senzor.
- Zobrazuje stav dveří pro soubor "klarka.csv" jako jednu spojenou přímku.

Použití:

- Upravte proměnnou `files`, aby obsahovala názvy vašich souborů bez přípony.
- Spusťte skript pro načtení a interpolaci dat, a následné vytvoření grafu.

Autor: Microsoft Copilot
