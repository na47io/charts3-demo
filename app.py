from flask import Flask, request, jsonify, render_template
import altair as alt
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes


# Sample data
def get_sample_data():
    return [
        {"x": 1, "y": 10, "category": "A", "value": 15, "date": "2023-01-01"},
        {"x": 2, "y": 15, "category": "B", "value": 8, "date": "2023-01-02"},
        {"x": 3, "y": 7, "category": "A", "value": 20, "date": "2023-01-03"},
        {"x": 4, "y": 20, "category": "B", "value": 12, "date": "2023-01-04"},
        {"x": 5, "y": 12, "category": "A", "value": 30, "date": "2023-01-05"},
        {"x": 6, "y": 18, "category": "B", "value": 18, "date": "2023-01-06"},
        {"x": 7, "y": 25, "category": "A", "value": 5, "date": "2023-01-07"},
        {"x": 8, "y": 15, "category": "B", "value": 22, "date": "2023-01-08"},
        {"x": 9, "y": 8, "category": "A", "value": 28, "date": "2023-01-09"},
        {"x": 10, "y": 14, "category": "B", "value": 15, "date": "2023-01-10"},
    ]


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/chart-spec")
def get_chart():
    """Generate an Altair chart specification based on query parameters."""
    # Get the chart type, fields and their types from the request
    chart_type = request.args.get("type", "line")
    x_field = request.args.get("x", "x")
    x_type = request.args.get("xType", "quantitative")
    y_field = request.args.get("y", "y")
    y_type = request.args.get("yType", "quantitative")
    color_field = request.args.get("color", None)
    color_type = request.args.get("colorType", "nominal")
    title = request.args.get("title", "")

    # Create base chart
    chart = None
    if chart_type == "bar":
        chart = alt.Chart().mark_bar()
    elif chart_type == "area":
        chart = alt.Chart().mark_area()
    elif chart_type == "line":
        chart = alt.Chart().mark_line()
    elif chart_type == "point" or chart_type == "scatter":
        chart = alt.Chart().mark_point()
    elif chart_type == "circle":
        chart = alt.Chart().mark_circle()
    elif chart_type == "boxplot":
        chart = alt.Chart().mark_boxplot()
    elif chart_type == "heatmap":
        chart = alt.Chart().mark_rect()
    else:
        # Default to bar chart
        chart = alt.Chart().mark_bar()

    # Start building the encoding
    encoding = {
        "x": {"field": x_field, "type": x_type},
        "y": {"field": y_field, "type": y_type},
    }

    # Add color encoding if specified
    if color_field:
        encoding["color"] = {"field": color_field, "type": color_type}

    # Add tooltip with all fields
    encoding["tooltip"] = [
        {"field": "x", "type": x_type},
        {"field": "y", "type": y_type},
    ]

    if color_field:
        encoding["tooltip"].append({"field": color_field, "type": color_type})

    # Create the chart with the encoding
    chart = chart.encode(**encoding)

    # Add title if provided
    if title:
        chart = chart.properties(title=title)

    # Add config for better appearance
    chart = (
        chart.configure_view(
            strokeWidth=0,
        )
        .configure_axis(grid=False)
        .properties(width="container", height=300)
    )

    # Convert to Vega-Lite spec
    spec = chart.to_dict()
    return jsonify(spec)


@app.route("/api/data.json")
def get_data():
    """Return sample data for the chart."""
    return jsonify(get_sample_data())


if __name__ == "__main__":
    app.run(debug=True)
