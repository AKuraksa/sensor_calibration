from flask import Flask, render_template, request, session, redirect, url_for
from modules.ploter import plot_figure
from modules.avg_senzor_time import process_files
from modules.least_squares import plot_calibrated_data

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
            fig = plot_figure(files, ref_file, show_points)
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


# New route for least squares calibration graph
@app.route('/least_squares', methods=['GET', 'POST'])
def least_squares():
    if request.method == 'POST':
        # Načteme názvy souborů a parametry z formuláře
        sensor_1 = request.form['sensor_1']
        sensor_2 = request.form['sensor_2']
        global_time_range = request.form.get('global_time_range', None)
        highlight_intervals = request.form.get('highlight_intervals', None)

        try:
            fig = plot_calibrated_data(f"./data_parsed/{sensor_1}.csv", f"./data_parsed/{sensor_2}.csv", global_time_range, highlight_intervals)

            # Check if the plot is None
            if fig is None:
                return render_template('least_squares.html', error="Chyba při vytváření grafu.")
            
            fig_html = fig.to_html(full_html=False)
            
        except Exception as e:
            return render_template('least_squares.html', error=f"Chyba: {str(e)}")

        return render_template('least_squares.html', plot=fig_html)

    return render_template('least_squares.html')


if __name__ == '__main__':
    app.run(debug=False)