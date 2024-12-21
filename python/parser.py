# Názvy vstupních souborů (zadejte seznam názvů bez přípony)
files = ["bile-28", "co-15", "klarka", "wifi-69"]
folder = "2024-12-10"

"""
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
"""

import csv
import json

# Funkce pro opravu formátování JSON
def fix_json_format(payload_str):
    try:
        payload_str = payload_str.strip('"')
        payload_str = payload_str.replace("'", '"')
        payload_str = payload_str.replace("None", 'null')
        return payload_str
    except Exception as e:
        print(f"Error fixing JSON: {e}")
        return None

# Funkce pro nahrazení tečky čárkou
def replace_dot_with_comma(value):
    if value != "N/A" and value != "Error":
        return str(value).replace(".", ",")
    return value

# Funkce pro určení typu souboru a extrakci dat
def parse_payload(file, row):
    try:
        payload_str = row["payload"]
        if not payload_str:
            raise ValueError("Prázdný nebo neplatný payload.")

        payload_str = fix_json_format(payload_str)
        if not payload_str.startswith('{') or not payload_str.endswith('}'):
            raise ValueError("Payload nemá platný JSON formát.")

        payload = json.loads(payload_str)

        # Rozpoznání formátu payloadu podle přítomných klíčů pro Klárku
        if file == "klarka" or "CO2Read" in payload:
            co2 = replace_dot_with_comma(payload.get("CO2Read", "N/A"))
            humidity = replace_dot_with_comma(payload.get("HumRead", "N/A"))
            temp = replace_dot_with_comma(payload.get("Temp1Read", "N/A"))
            door_open = payload.get("DoorOpen", "N/A")
            
            # Kontrola, zda obsahuje hodnoty 'N/D'
            if "N/D" in [co2, humidity, temp]:
                raise ValueError("Řádek obsahuje hodnotu 'N/D'.")
            
            return {
                "co2": co2,
                "humidity": humidity,
                "temp": temp,
                "door_open": door_open
            }
        elif "uplink_message" in payload:
            if "decoded_payload" in payload["uplink_message"]:
                decoded_payload = payload["uplink_message"]["decoded_payload"]
                if "decoded" in decoded_payload:
                    decoded = decoded_payload["decoded"]
                    return {
                        "co2": "null",
                        "humidity": replace_dot_with_comma(decoded.get("humidity", "N/A")),
                        "temp": replace_dot_with_comma(decoded.get("temperature", "N/A"))
                    }
                elif "msg" in decoded_payload:
                    msg_parts = decoded_payload["msg"].split(';')
                    if len(msg_parts) >= 4:
                        return {
                            "co2": replace_dot_with_comma(msg_parts[1]),
                            "humidity": replace_dot_with_comma(msg_parts[3]),
                            "temp": replace_dot_with_comma(msg_parts[2])
                        }
            else:
                return None  # Záznam se smaže, pokud "uplink_message" neexistuje
        raise ValueError("Neznámý formát payloadu.")
    except (json.JSONDecodeError, ValueError, KeyError) as e:
        print(f"Chyba parsování JSON: {e}\nPayload: {repr(payload_str)}")
        return None

# Iterace přes všechny soubory
for file in files:
    input_file = f"./data_raw/{folder}/{file}.csv"
    output_file = f"./data_parsed/{file}.csv"

    # Načtení dat ze vstupního CSV
    with open(input_file, mode="r", encoding="utf-8") as infile:
        reader = csv.DictReader(infile)

        # Přidání nových sloupců do hlavičky
        fieldnames = ["id", "date", "time", "topic", "co2", "humidity", "temp"]
        if file == "klarka":
            fieldnames.append("door_open")
        rows = []
        deleted_count = 0

        for row in reader:
            try:
                time_value = row["time"]
                if time_value:
                    date, time = time_value.split(" ")
                    row["date"] = date
                    row["time"] = time
                else:
                    row["date"] = "N/A"
                    row["time"] = "N/A"

                # Zpracování payloadu
                parsed_data = parse_payload(file, row)
                if parsed_data is None:
                    deleted_count += 1
                    continue

                row.update(parsed_data)
            except Exception as e:
                print(f"Obecná chyba při zpracování řádku: {e}")
                deleted_count += 1
                continue

            rows.append(row)

    # Uložení upravených dat do výstupního CSV
    with open(output_file, mode="w", encoding="utf-8", newline="") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            # Odstranění klíčů, které nejsou v fieldnames
            filtered_row = {key: row[key] for key in fieldnames if key in row}
            writer.writerow(filtered_row)

    print(f"Data byla úspěšně uložena do souboru {output_file}.")
    print(f"Počet smazaných řádků: {deleted_count}.")