from flask import Flask, request, render_template, jsonify
import altair as alt
from flask_cors import CORS
import pandas as pd
import numpy as np
import json

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Chart types supported by the application
CHART_TYPES = {
    "line": "Line Chart",
    "bar": "Bar Chart",
    "point": "Scatter Plot",
    "area": "Area Chart",
    "boxplot": "Box Plot",
    "heatmap": "Heatmap"
}

# Data types for Altair encodings
DATA_TYPES = {
    "quantitative": "Quantitative",
    "nominal": "Nominal", 
    "ordinal": "Ordinal",
    "temporal": "Time"
}

def generate_sample_dataframe():
    """Generate a simple dataframe with two columns for visualization."""
    # Create a simple dataframe with x and y values
    return pd.DataFrame({
        "x": np.arange(1, 101),
        "y": np.random.normal(50, 15, 100)
    })

def create_chart(chart_type, x_field, x_type, y_field, y_type, color_field=None, color_type="nominal", title=""):
    """Create an Altair chart based on parameters."""
    # Create base chart based on chart type
    if chart_type == "bar":
        chart = alt.Chart().mark_bar()
    elif chart_type == "area":
        chart = alt.Chart().mark_area()
    elif chart_type == "line":
        chart = alt.Chart().mark_line()
    elif chart_type == "point" or chart_type == "scatter":
        chart = alt.Chart().mark_circle()
    elif chart_type == "boxplot":
        chart = alt.Chart().mark_boxplot()
    elif chart_type == "heatmap":
        chart = alt.Chart().mark_rect()
    else:
        # Default to line chart
        chart = alt.Chart().mark_line()

    # Add encodings with explicit types
    encoding = {
        "x": {"field": x_field, "type": x_type},
        "y": {"field": y_field, "type": y_type},
    }

    if color_field:
        encoding["color"] = {"field": color_field, "type": color_type}

    # Add tooltip
    tooltip_fields = [
        {"field": x_field, "type": x_type},
        {"field": y_field, "type": y_type}
    ]
    
    if color_field:
        tooltip_fields.append({"field": color_field, "type": color_type})
        
    encoding["tooltip"] = tooltip_fields

    # Apply encoding to chart
    chart = chart.encode(**encoding)
    
    # Add title if provided
    if title:
        chart = chart.properties(title=title)

    # Add config for better appearance
    chart = chart.configure_view(
        strokeWidth=0,
    ).configure_axis(
        grid=False
    ).properties(
        width="container",
        height=300
    )
    
    return chart


@app.route("/", methods=["GET", "POST"])
def index():
    # Get the dataframe
    df = generate_sample_dataframe()
    available_fields = list(df.columns)
    
    # Default chart parameters
    chart_type = "line"
    x_field = "x"
    x_type = "quantitative"
    y_field = "y" 
    y_type = "quantitative"
    color_field = ""
    color_type = "nominal"
    title = ""
    
    # If form was submitted, get the chart parameters
    if request.method == "POST":
        chart_type = request.form.get("chart_type", chart_type)
        x_field = request.form.get("x_field", x_field)
        x_type = request.form.get("x_type", x_type)
        y_field = request.form.get("y_field", y_field)
        y_type = request.form.get("y_type", y_type)
        color_field = request.form.get("color_field", color_field)
        color_type = request.form.get("color_type", color_type)
        title = request.form.get("title", title)
    
    # Create the chart
    chart = create_chart(
        chart_type, 
        x_field, 
        x_type, 
        y_field, 
        y_type, 
        color_field if color_field else None, 
        color_type,
        title
    )
    
    # Generate chart spec and HTML for embedding
    chart_spec = chart.to_dict()
    chart_json = json.dumps(chart_spec)
    
    # Convert dataframe to JSON for display
    df_json = df.to_json(orient='records')
    
    return render_template(
        "index.html",
        chart_types=CHART_TYPES,
        data_types=DATA_TYPES,
        available_fields=available_fields,
        chart_json=chart_json,
        data_json=df_json,
        selected_chart_type=chart_type,
        selected_x_field=x_field,
        selected_x_type=x_type,
        selected_y_field=y_field,
        selected_y_type=y_type,
        selected_color_field=color_field,
        selected_color_type=color_type,
        selected_title=title
    )


@app.route("/api/data.json")
def get_data():
    """Return the dataframe as JSON for the chart."""
    df = generate_sample_dataframe()
    return df.to_json(orient='records')


if __name__ == "__main__":
    app.run(debug=True)