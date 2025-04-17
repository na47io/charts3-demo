from flask import Flask, request, jsonify, render_template
import altair as alt
from flask_cors import CORS  # You'll need this for cross-origin requests

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/chart-spec", methods=["GET"])
def get_chart_spec():
    # Get parameters from the request
    x_field = request.args.get("x", "x")
    y_field = request.args.get("y", "y")
    color_field = request.args.get("color", None)
    chart_type = request.args.get("type", "line")

    # Create base chart
    if chart_type == "line":
        chart = alt.Chart().mark_line()
    elif chart_type == "bar":
        chart = alt.Chart().mark_bar()
    elif chart_type == "point":
        chart = alt.Chart().mark_circle()
    else:
        chart = alt.Chart().mark_line()

    # Add encodings with explicit types
    encodings = {
        "x": alt.X(x_field, type="quantitative"),
        "y": alt.Y(y_field, type="quantitative"),
    }

    if color_field:
        # Explicitly specify the type for color
        encodings["color"] = alt.Color(color_field, type="nominal")

    chart = chart.encode(**encodings)

    # Convert to Vega-Lite spec
    spec = chart.to_dict()

    return jsonify(spec)


# Sample data endpoint
@app.route("/api/data.json")
def get_data():
    # For demo purposes, return some sample data
    data = [
        {"x": 1, "y": 10, "category": "A"},
        {"x": 2, "y": 15, "category": "B"},
        {"x": 3, "y": 7, "category": "A"},
        {"x": 4, "y": 20, "category": "B"},
        {"x": 5, "y": 12, "category": "A"},
    ]
    return jsonify(data)


if __name__ == "__main__":
    app.run(debug=True)
