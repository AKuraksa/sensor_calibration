import csv
import json
import re

# Název vstupního a výstupního souboru
file = "klarka.csv"

input_file = f"./data_raw/{file}"
output_file = f"./data_parsed/{file}"

# Funkce pro opravu formátování JSON
def fix_json_format(payload_str): 
    try: 
        # Remove outer quotes 
        payload_str = payload_str.strip('"') 
        # Replace single quotes with double quotes 
        payload_str = payload_str.replace("'", '"') 
        payload_str = payload_str.replace("None", '""')
        # Ensure the final payload is valid JSON 
        return payload_str 
    except Exception as e: 
        print(f"Error fixing JSON: {e}") 
        return None



# Načtení dat ze vstupního CSV
with open(input_file, mode="r", encoding="utf-8") as infile:
    reader = csv.DictReader(infile)
    
    # Přidání nových sloupců do hlavičky
    fieldnames = ["id", "time", "topic", "co2", "hum", "temp", "payload"]
    rows = []

    for row in reader:
        try:
            # Načtení JSON objektu z pole payload
            payload_str = row["payload"]
            if payload_str:
                payload_str = fix_json_format(payload_str)

                # Validace JSON před parsováním
                if not payload_str.startswith('{') or not payload_str.endswith('}'):
                    raise ValueError("Payload nemá platný JSON formát (chybí složené závorky).")

                payload = json.loads(payload_str)

                # Extrakce hodnot
                co2_read = payload.get("CO2Read", "N/A")
                hum_read = payload.get("HumRead", "N/A")
                temp1_read = payload.get("Temp1Read", "N/A")

                # Přidání hodnot do nových sloupců
                row["co2"] = co2_read
                row["hum"] = hum_read
                row["temp"] = temp1_read
            else:
                raise ValueError("Prázdný nebo neplatný payload.")
        except (json.JSONDecodeError, ValueError) as e:
            # Vypsání chybového hlášení
            error_msg = f"Chyba parsování JSON: {e}\nDélka payloadu: {len(payload_str)}\nProblematic payload: {repr(payload_str)}\n"
            print(error_msg)

            # Zapište 'Error' do nových sloupců
            row["co2"] = "Error"
            row["hum"] = "Error"
            row["temp"] = "Error"

        rows.append(row)

# Uložení upravených dat do výstupního CSV
with open(output_file, mode="w", encoding="utf-8", newline="") as outfile:
    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f"Data byla úspěšně uložena do souboru {output_file}.")