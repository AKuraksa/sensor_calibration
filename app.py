from flask import Flask, render_template, request, session, redirect, url_for
from modules.ploter import plot_figure
from modules.avg_senzor_time import process_files
from modules.least_squares import plot_calibrated_data
import os
from flask_session import Session

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Configure server-side session
app.config['SESSION_TYPE'] = 'filesystem'  # Store sessions in the file system
app.config['SESSION_FILE_DIR'] = './flask_sessions'  # Directory to store session files
app.config['SESSION_PERMANENT'] = False  # Sessions will not persist when the server restarts
Session(app)

# Nastavení adresáře pro CSV soubory
DATA_DIR = './data_parsed/'

try:
    choice = [os.path.splitext(f)[0] for f in os.listdir(DATA_DIR) if f.endswith('.csv')]
except FileNotFoundError:
    choice = []

# Degub choice
#print("Files:", choice)

@app.context_processor
def inject_notes():
    hostname = request.host
    notes = session.get('notes', {}).get(hostname, [])
    return dict(notes=notes)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/progress_graph', methods=['GET', 'POST'])
def progress_graph():
    if request.method == 'POST':
        # Process graph generation
        files = request.form['files'].split(',')
        files = [file.strip() for file in files]
        ref_file = request.form.get('ref_file', '').strip()
        show_points = 'show_points' in request.form

        if ref_file and ref_file not in files:
            return render_template('progress_graph.html', choice=choice, error="Reference file is not in the provided list of files.")

        try:
            fig = plot_figure(files, ref_file, show_points)
            session['last_graph'] = fig.to_html(full_html=False)
        except Exception as e:
            return render_template('progress_graph.html', choice=choice, error=str(e))

        # Process intervals
        try:
            intervals = process_files(files)
            session['intervals'] = "<ul>" + "".join([f"<li>{file}: {interval}</li>" for file, interval in intervals.items()]) + "</ul>"
        except Exception as e:
            session['intervals'] = f"Error calculating intervals: {str(e)}"

        return redirect(url_for('progress_graph'))

    graph_html = session.get('last_graph', None)
    intervals_html = session.get('intervals', None)
    return render_template('progress_graph.html', choice=choice, plot=graph_html, intervals=intervals_html)


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
                return render_template('least_squares.html', choice=choice, error="Chyba při vytváření grafu.")
            
            fig_html = fig.to_html(full_html=False)
            
        except Exception as e:
            return render_template('least_squares.html', choice=choice, error=f"Chyba: {str(e)}")

        
        return render_template('least_squares.html', choice=choice, plot=fig_html)

    return render_template('least_squares.html', choice=choice)

# Adding notepad functionality
@app.route('/notepad', methods=['POST'])
def notepad():
    if 'notes' not in session:
        session['notes'] = {}

    hostname = request.host
    data = request.get_json()
    note = data.get('note', '')

    if not note.strip():
        return 'Note cannot be empty!', 400

    if hostname not in session['notes']:
        session['notes'][hostname] = []
    session['notes'][hostname].append(note)
    session.modified = True
    return '', 204  # Return a "No Content" response

@app.route('/delete_notes', methods=['POST'])
def delete_notes():
    if 'notes' not in session:
        session['notes'] = {}

    hostname = request.host
    if hostname in session['notes']:
        data = request.get_json()
        notes_to_delete = data.get('notes', [])
        session['notes'][hostname] = [note for note in session['notes'][hostname] if note not in notes_to_delete]
        session.modified = True

    return '', 204  # Return a "No Content" response

if __name__ == '__main__':
    app.run(debug=True)