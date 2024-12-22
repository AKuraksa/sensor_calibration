from flask import Flask, render_template, request, jsonify
from python.ploter import plot_data
from python.least_squares import plot_calibrated_data
import os

app = Flask(__name__)

# Endpoint pro hlavní stránku
@app.route('/')
def index():
    files = os.listdir('./data_parsed')  # Získání seznamu dostupných souborů
    return render_template('index.html', files=files)

# Endpoint pro zpracování výběru souborů a generování grafů
@app.route('/generate_graphs', methods=['POST'])
def generate_graphs():
    selected_files = request.json.get('selected_files', [])
    if not selected_files:
        return jsonify({'error': 'Žádné soubory nebyly vybrány.'}), 400

    # Generování grafů
    try:
        plot_data(selected_files)  # První graf
        plot_calibrated_data(selected_files[0], selected_files[1])  # Druhý graf (například pro kalibraci)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    return jsonify({'message': 'Grafy byly úspěšně vygenerovány.'})

if __name__ == '__main__':
    app.run(debug=True)
