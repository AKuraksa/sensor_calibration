## parser.py

Tento skript slouží k vyčištění a zpracování surových dat ze souboru CSV.

Funkce:

- Načítá data ze složky `data_raw` podle zadaného názvu souboru.
- Zpracovává sloupec `payload`, který obsahuje data ve formátu JSON, a extrahuje potřebné informace:

  - Hodnoty CO2, vlhkosti a teploty.
- Pokud je záznam neplatný nebo chybí důležité informace, je odstraněn.
- Rozděluje časový údaj do samostatných sloupců `date` (datum) a `time` (čas).
- Upravená data jsou uložena do nové složky `data_parsed` se stejným názvem souboru.

Statistiky:

- Na konci zpracování skript zobrazí, kolik záznamů bylo úspěšně zpracováno a kolik bylo odstraněno.

Použití:

- Upravte proměnnou `file`, aby odpovídala názvu vašeho souboru bez složky a přípony.
- Spusťte skript pro vyčištění a uložení dat.

Autor: OpenAI ChatGPT

## ploter.py

Tento skript je určen k načítání, interpolaci dat ze souborů CSV a k vytváření interaktivních grafů teplot pomocí knihovny **Plotly**. Program umožňuje porovnání dat ze senzorů a zahrnuje specifickou podporu pro referenční senzor, u kterého se zobrazí tolerance ±0,5°C.

---

### Funkce programu

1. **Načítání dat ze souborů CSV**

   - Skript načítá soubory ze složky `data_parsed` podle názvů zadaných uživatelem.
   - Soubory musí obsahovat minimálně následující sloupce:
     - `time` (čas ve formátu HH:MM:SS)
     - `temp` (teplota)
   - Nepovinné sloupce:
     - `door_open` (stav dveří).
2. **Zpracování a validace dat**

   - Sloupec `temp` je zpracován:
     - Nahrazení hodnot `N/D` (neplatných záznamů) hodnotou `NaN`.
     - Převod teploty z textového formátu (s desetinnou čárkou) na číselnou hodnotu (s desetinnou tečkou).
   - Záznamy s neplatnými daty (`NaN`) jsou odstraněny.
3. **Rozdělení časových údajů**

   - Časové údaje jsou načteny z `time` a převedeny do formátu pro analýzu.
   - Data jsou interpolována na jednotlivé sekundy, aby bylo možné plynulé vykreslení.
4. **Interpolace teplotních dat**

   - Program využívá lineární interpolaci pro dopočítání hodnot mezi měřeními.
   - Data z referenčního souboru zahrnují toleranci ±0,5°C jako samostatné linie.
5. **Vytváření interaktivních grafů**

   - Každý senzor je vykreslen jako samostatná linie.
   - Referenční senzor má toleranční pásmo ±0,5°C (zobrazeno čárkovanou čarou).
   - Pokud je zadaný `door_open`, je jeho stav zobrazen jako grafická stopa.
6. **Zobrazení výsledků**

   - Program zobrazí interaktivní graf s:
     - Časovou osou.
     - Teplotními hodnotami.
     - Volitelně bodovými měřeními pro vizuální kontrolu.

---

### Jak program pracuje se souborem

1. **Načtení souboru:** Program otevře CSV soubor ze složky `data_parsed` podle zadaného názvu.
2. **Ověření obsahu:** Program kontroluje, zda soubor obsahuje požadované sloupce (`time`, `temp`). Pokud některý chybí, zobrazí varování a přejde na další soubor.
3. **Předzpracování dat:**

   - Neplatné hodnoty teploty (`N/D`) jsou nahrazeny `NaN`.
   - Hodnoty `NaN` jsou odstraněny.
   - Časový sloupec `time` je převeden na formát `datetime`.
4. **Výpočet interpolace:**

   - Vypočítá se interpolace teploty na základě časového intervalu.
   - Pro referenční soubor se přidá tolerance ±0,5°C jako dvě další interpolované linie.
5. **Kontrola rozsahu času:**

   - Program určí minimální a maximální čas napříč všemi soubory.
   - Data z každého souboru jsou přizpůsobena společnému časovému rozsahu.
6. **Vykreslení:**

   - Všechna data jsou vykreslena do jednoho interaktivního grafu.
   - Pokud je `door_open` ve vstupních datech, jeho stav je zobrazen jako dodatečná čára.
7. **Zobrazení grafu:**

   - Program zobrazí výsledný graf s možností interakce (např. zobrazení konkrétních hodnot).

---

### Použití programu

1. Připravte soubory CSV ve složce `data_parsed`. Každý soubor by měl obsahovat alespoň sloupce `time` a `temp`.
2. Spusťte program.
3. Zadejte názvy souborů (oddělené čárkou, bez přípony).
4. Zadejte referenční soubor (pokud existuje).
5. Program vykreslí interaktivní graf, který můžete analyzovat.

---

### Autorství

Tento skript byl vytvořen a upraven jako uživatelský nástroj s přispěním asistenta OpenAI a Microsoft Copilot.

## tools.py

Knihovna repetitivních kódů
