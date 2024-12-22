from flask import Flask, render_template, request
from modules.ploter import plot_figure, validate_files
import os

app = Flask(__name__)

# Nastavení adresáře pro CSV soubory
DATA_DIR = './data_parsed/'

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Načteme názvy souborů a parametry z formuláře
        files = request.form['files'].split(',')
        files = [file.strip() for file in files]
        ref_file = request.form['ref_file'].strip()
        show_points = 'show_points' in request.form

        # Zkontrolujeme, jestli je referenční soubor v seznamu
        if ref_file and ref_file not in files:
            return render_template('index.html', error="Reference file is not in the provided list of files.")

        # Generování grafu pomocí funkce z modulu ploter
        file_paths = validate_files(files)
        fig = plot_figure(file_paths, ref_file, show_points)
        fig_html = fig.to_html(full_html=False)

        # Zobrazení generovaného grafu
        return render_template('index.html', plot=fig_html)

    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)