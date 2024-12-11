import csv
import json
import re

# Název vstupního a výstupního souboru
file = "wifi-69.csv"

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
    fieldnames = ["id", "time", "topic", "co2", "humidity", "temp"]
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
                if 'uplink_message' in payload and 'decoded_payload' in payload['uplink_message']:
                    decoded_payload = payload["uplink_message"]["decoded_payload"]

                    if 'msg' in decoded_payload:
                        msg = decoded_payload["msg"]
                        msg_parts = msg.split(';')
                        if len(msg_parts) >= 4:
                            co2_read = msg_parts[1]
                            hum_read = msg_parts[3]
                            temp1_read = msg_parts[2]
                        else:
                            co2_read, hum_read, temp1_read = "N/A", "N/A", "N/A"
                    else:
                        co2_read, hum_read, temp1_read = "N/A", "N/A", "N/A"
                else:
                    co2_read, hum_read, temp1_read = "N/A", "N/A", "N/A"

                # Přidání hodnot do nových sloupců
                row["co2"] = co2_read
                row["humidity"] = hum_read
                row["temp"] = temp1_read
            else:
                raise ValueError("Prázdný nebo neplatný payload.")
        except (json.JSONDecodeError, ValueError) as e:
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
