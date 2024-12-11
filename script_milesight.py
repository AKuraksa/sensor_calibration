import csv
import json

# Název vstupního a výstupního souboru
file = "bile-28.csv"

input_file = f"./data_raw/{file}"
output_file = f"./data_parsed/{file}"

# Funkce pro opravu formátování JSON a nahrazení None prázdným řetězcem
def fix_json_format(payload_str):
    try:
        # Replace None with an empty string
        payload_str = payload_str.replace('None', '""')
        return payload_str
    except Exception as e:
        print(f"Error fixing JSON: {e}")
        return None

# Načtení dat ze vstupního CSV
with open(input_file, mode="r", encoding="utf-8") as infile:
    reader = csv.DictReader(infile)
    
    # Přidání nových sloupců do hlavičky
    fieldnames = ["id", "time", "topic", "co2", "humidity", "temp"]
    rows = []

    for row in reader:
        try:
            # Načtení JSON objektu z pole payload
            payload_str = row["payload"]
            if payload_str:
                payload_str = fix_json_format(payload_str)

                payload = json.loads(payload_str)

                # Extract the nested values
                decoded_payload = payload["uplink_message"]["decoded_payload"]["decoded"]
                humidity = decoded_payload.get("humidity", "N/A")
                temperature = decoded_payload.get("temperature", "N/A")

                # Přidání hodnot do nových sloupců
                row["co2"] = None
                row["humidity"] = humidity
                row["temp"] = temperature
            else:
                raise ValueError("Prázdný nebo neplatný payload.")
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            # Vypsání chybového hlášení
            error_msg = f"Chyba parsování JSON: {e}\nDélka payloadu: {len(payload_str)}\nProblematic payload: {repr(payload_str)}\n"
            print(error_msg)

            # Zapište 'Error' do nových sloupců
            row["co2"] = "Error"
            row["humidity"] = "Error"
            row["temp"] = "Error"

        # Odstranění pole payload
        if "payload" in row:
            del row["payload"]

        rows.append(row)

# Uložení upravených dat do výstupního CSV
with open(output_file, mode="w", encoding="utf-8", newline="") as outfile:
    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f"Data byla úspěšně uložena do souboru {output_file}.")