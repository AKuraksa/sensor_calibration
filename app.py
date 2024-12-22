from flask import Flask, render_template, request
from modules.ploter import plot_figure
from modules.avg_senzor_time import process_files
from modules.tools import validate_files

app = Flask(__name__)

# Nastavení adresáře pro CSV soubory
DATA_DIR = './data_parsed/'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/progress_graph', methods=['GET', 'POST'])
def progress_graph():
    if request.method == 'POST':
        # Načteme názvy souborů a parametry z formuláře
        files = request.form['files'].split(',')
        files = [file.strip() for file in files]
        ref_file = request.form['ref_file'].strip()
        show_points = 'show_points' in request.form

        # Zkontrolujeme, jestli je referenční soubor v seznamu
        if ref_file and ref_file not in files:
            return render_template('progress_graph.html', error="Reference file is not in the provided list of files.")

        # Generování grafu pomocí funkce z modulu ploter
        try:
            file_paths = validate_files(files)
            fig = plot_figure(file_paths, ref_file, show_points)
            fig_html = fig.to_html(full_html=False)
        except Exception as e:
            return render_template('progress_graph.html', error=str(e))

        # Získáme průměrné intervaly snímání senzorů
        try:
            intervals = process_files(files)
            intervals_html = "<ul>" + "".join([f"<li>{file}: {interval}</li>" for file, interval in intervals.items()]) + "</ul>"
        except Exception as e:
            intervals_html = f"Error calculating intervals: {str(e)}"

        # Zobrazení generovaného grafu a průměrných intervalů
        return render_template('progress_graph.html', plot=fig_html, intervals=intervals_html)

    return render_template('progress_graph.html')


if __name__ == '__main__':
    app.run(debug=False)