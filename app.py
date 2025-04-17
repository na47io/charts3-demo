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
    "heatmap": "Heatmap",
    "pie": "Pie Chart",
    "histogram": "Histogram"
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
        "x": np.arange(1, 10001),
        "y": np.random.normal(50, 15, 10000)
    })

def create_chart(chart_type, x_field, x_type, y_field, y_type, color_field=None, color_type="nominal", 
                title="", bin_parameters=None, aggregate_function="count"):
    """Create an Altair chart based on parameters.
    
    Supports both regular charts and aggregate charts like histograms and pie charts.
    """
    # Handle aggregate charts (pie, histogram)
    if chart_type in ["pie", "histogram"]:
        return create_aggregate_chart(
            chart_type, x_field, x_type, y_field, y_type, 
            color_field, color_type, title, bin_parameters, aggregate_function
        )
    
    # Create base chart based on chart type (non-aggregate)
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


def create_aggregate_chart(chart_type, x_field, x_type, y_field, y_type, color_field=None, color_type="nominal",
                         title="", bin_parameters=None, aggregate_function="count"):
    """Create aggregate charts like pie charts and histograms."""
    
    if chart_type == "histogram":
        # For histograms, we need to bin the x field
        binned_x = {"field": x_field, "type": x_type, "bin": True}
        if bin_parameters:
            # If bin parameters are provided, use them
            binned_x["bin"] = bin_parameters
            
        chart = alt.Chart().mark_bar().encode(
            x=binned_x,
            y=alt.Y(aggregate=aggregate_function, title=f"{aggregate_function.title()} of Records"),
            tooltip=[
                {"field": x_field, "type": x_type, "bin": True},
                {"aggregate": aggregate_function, "title": f"{aggregate_function.title()} of Records"}
            ]
        )
        
        if color_field:
            chart = chart.encode(color={"field": color_field, "type": color_type})
            
    elif chart_type == "pie":
        # For pie charts, we need a theta field (angle) for the slice size
        # and a color field for the slice identity
        # If no color field is provided, use the x field
        theta_field = y_field if y_field else x_field
        slice_field = color_field if color_field else x_field
        slice_type = color_type if color_field else x_type
        
        chart = alt.Chart().mark_arc().encode(
            theta=alt.Theta(field=theta_field, type=y_type, aggregate=aggregate_function),
            color=alt.Color(field=slice_field, type=slice_type),
            tooltip=[
                {"field": slice_field, "type": slice_type},
                {"field": theta_field, "type": y_type, "aggregate": aggregate_function}
            ]
        )
    else:
        # Default to a count aggregation bar chart if an unknown aggregate type is specified
        chart = alt.Chart().mark_bar().encode(
            x={"field": x_field, "type": x_type},
            y=alt.Y(aggregate=aggregate_function, title=f"{aggregate_function.title()} of Records"),
            tooltip=[
                {"field": x_field, "type": x_type},
                {"aggregate": aggregate_function, "title": f"{aggregate_function.title()} of Records"}
            ]
        )
        
        if color_field:
            chart = chart.encode(color={"field": color_field, "type": color_type})
    
    # Add title if provided
    if title:
        chart = chart.properties(title=title)
        
    # Add config for better appearance
    chart = chart.configure_view(
        strokeWidth=0,
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
    
    # Aggregation functions available for aggregate charts
    aggregate_functions = {
        "count": "Count",
        "sum": "Sum",
        "mean": "Average",
        "median": "Median",
        "min": "Minimum", 
        "max": "Maximum"
    }
    
    # Default chart parameters
    chart_type = "line"
    x_field = "x"
    x_type = "quantitative"
    y_field = "y" 
    y_type = "quantitative"
    color_field = ""
    color_type = "nominal"
    title = ""
    aggregate_function = "count"
    bin_step = 10  # Default bin size for histograms
    
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
        
        # Get aggregation parameters if provided
        aggregate_function = request.form.get("aggregate_function", aggregate_function)
        bin_step_str = request.form.get("bin_step", str(bin_step))
        try:
            bin_step = float(bin_step_str)
        except ValueError:
            bin_step = 10  # Default if invalid input
    
    # Set up bin parameters for histogram
    bin_parameters = {"maxbins": 20}  # Default binning
    if chart_type == "histogram" and bin_step > 0:
        bin_parameters = {"step": bin_step}
        
    # Create the chart
    chart = create_chart(
        chart_type=chart_type, 
        x_field=x_field, 
        x_type=x_type, 
        y_field=y_field, 
        y_type=y_type, 
        color_field=color_field if color_field else None, 
        color_type=color_type,
        title=title,
        bin_parameters=bin_parameters,
        aggregate_function=aggregate_function
    )
    
    # Generate chart spec and HTML for embedding
    chart_spec = chart.to_dict()
    chart_json = json.dumps(chart_spec)
    
    return render_template(
        "index.html",
        chart_types=CHART_TYPES,
        data_types=DATA_TYPES,
        aggregate_functions=aggregate_functions,
        available_fields=available_fields,
        chart_json=chart_json,
        selected_chart_type=chart_type,
        selected_x_field=x_field,
        selected_x_type=x_type,
        selected_y_field=y_field,
        selected_y_type=y_type,
        selected_color_field=color_field,
        selected_color_type=color_type,
        selected_title=title,
        selected_aggregate_function=aggregate_function,
        selected_bin_step=bin_step,
        is_aggregate_chart=chart_type in ["pie", "histogram"]
    )


@app.route("/api/data.json")
def get_data():
    """Return the dataframe as JSON for the chart."""
    df = generate_sample_dataframe()
    return df.to_json(orient='records')


if __name__ == "__main__":
    app.run(debug=True)
