from flask import Flask, render_template, request
import plotly.io as pio
from python.ploter import plot_data  # Import obou funkcí
from python.least_squares import plot_calibrated_data

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    graph_html = None

    if request.method == "POST":
        # Zjištění, jaký graf chce uživatel vykreslit
        graph_type = request.form.get("graph_type")
        
        # Předání parametrů pro první graf (plot_data)
        if graph_type == "temperature":
            files = request.form.get("files").split(",")  # Očekáváme seznam souborů oddělených čárkou
            graph_html = plot_data_for_web(files)

        # Předání parametrů pro druhý graf (plot_calibrated_data)
        elif graph_type == "calibration":
            sensor_1 = request.form.get("sensor_1")
            sensor_2 = request.form.get("sensor_2")
            global_time_range = request.form.get("time_range")
            highlight_intervals_input = request.form.get("highlight_intervals")
            global_time_range = global_time_range.split(",") if global_time_range else None
            highlight_intervals = [tuple(interval.split(",")) for interval in highlight_intervals_input.split(";")] if highlight_intervals_input else []

            graph_html = plot_calibrated_data_for_web(sensor_1, sensor_2, global_time_range, highlight_intervals)

    return render_template("index.html", graph=graph_html)

def plot_data_for_web(files):
    fig = plot_data(files)  # Používáme stávající funkci plot_data
    return pio.to_html(fig, full_html=False)  # Převeď na HTML pro Flask

def plot_calibrated_data_for_web(sensor_1, sensor_2, global_time_range, highlight_intervals):
    fig = plot_calibrated_data(sensor_1, sensor_2, global_time_range, highlight_intervals)  # Používáme novou funkci plot_calibrated_data
    return pio.to_html(fig, full_html=False)  # Převeď na HTML pro Flask

if __name__ == "__main__":
    app.run(debug=True)