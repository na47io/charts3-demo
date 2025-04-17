from flask import Flask, request, render_template, jsonify, redirect, url_for
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

# Aggregation functions available for aggregate charts
AGGREGATE_FUNCTIONS = {
    "count": "Count",
    "sum": "Sum",
    "mean": "Average",
    "median": "Median",
    "min": "Minimum", 
    "max": "Maximum"
}

def generate_sample_dataframe():
    """Generate a simple dataframe with two columns for visualization."""
    # Create a simple dataframe with x and y values
    return pd.DataFrame({
        "x": np.arange(1, 101),
        "y": np.random.normal(50, 15, 100)
    })

def create_standard_chart(chart_type, x_field, x_type, y_field, y_type, color_field=None, color_type="nominal", title=""):
    """Create a standard (non-aggregate) chart based on parameters."""
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


def create_pie_chart(slice_field, slice_type, value_field=None, value_type="quantitative", 
                   aggregate_function="count", title=""):
    """Create a pie chart."""
    # For pie charts, we need a theta field (angle) for the slice size
    theta_field = value_field if value_field else slice_field
    
    chart = alt.Chart().mark_arc().encode(
        theta=alt.Theta(field=theta_field, type=value_type, aggregate=aggregate_function),
        color=alt.Color(field=slice_field, type=slice_type),
        tooltip=[
            {"field": slice_field, "type": slice_type},
            {"field": theta_field, "type": value_type, "aggregate": aggregate_function}
        ]
    )
    
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


def create_histogram(x_field, x_type, color_field=None, color_type="nominal",
                   aggregate_function="count", bin_step=10, title=""):
    """Create a histogram."""
    # For histograms, we need to bin the x field
    bin_parameters = {"step": bin_step} if bin_step > 0 else {"maxbins": 20}
    
    binned_x = {"field": x_field, "type": x_type, "bin": bin_parameters}
        
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


@app.route("/")
def index():
    """Main entry point - redirects to default chart type."""
    return redirect(url_for('get_chart_page', chart_type='line'))


@app.route("/chart/<chart_type>", methods=["GET", "POST"])
def get_chart_page(chart_type):
    """Route handler for all chart types."""
    # Validate chart type
    if chart_type not in CHART_TYPES:
        return redirect(url_for('get_chart_page', chart_type='line'))
        
    # Get the dataframe for field options
    df = generate_sample_dataframe()
    available_fields = list(df.columns)
    
    # Route to appropriate chart handler
    if chart_type == "pie":
        return handle_pie_chart_request(available_fields, request)
    elif chart_type == "histogram":
        return handle_histogram_request(available_fields, request)
    else:
        return handle_standard_chart_request(chart_type, available_fields, request)


def handle_standard_chart_request(chart_type, available_fields, request):
    """Handle standard (non-aggregate) chart requests."""
    # Default chart parameters for standard charts
    x_field = "x"
    x_type = "quantitative"
    y_field = "y" 
    y_type = "quantitative"
    color_field = ""
    color_type = "nominal"
    title = ""
    
    # If form was submitted, get the chart parameters
    if request.method == "POST":
        x_field = request.form.get("x_field", x_field)
        x_type = request.form.get("x_type", x_type)
        y_field = request.form.get("y_field", y_field) 
        y_type = request.form.get("y_type", y_type)
        color_field = request.form.get("color_field", color_field)
        color_type = request.form.get("color_type", color_type)
        title = request.form.get("title", title)
    
    # Create the chart
    chart = create_standard_chart(
        chart_type=chart_type, 
        x_field=x_field, 
        x_type=x_type, 
        y_field=y_field, 
        y_type=y_type, 
        color_field=color_field if color_field else None, 
        color_type=color_type,
        title=title
    )
    
    # Generate chart spec
    chart_spec = chart.to_dict()
    chart_json = json.dumps(chart_spec)
    
    # Render the template with only the form fields needed for standard charts
    return render_template(
        "standard_chart.html",
        chart_types=CHART_TYPES,
        data_types=DATA_TYPES,
        available_fields=available_fields,
        chart_json=chart_json,
        selected_chart_type=chart_type,
        selected_x_field=x_field,
        selected_x_type=x_type,
        selected_y_field=y_field,
        selected_y_type=y_type,
        selected_color_field=color_field,
        selected_color_type=color_type,
        selected_title=title
    )


def handle_pie_chart_request(available_fields, request):
    """Handle pie chart requests."""
    # Default chart parameters for pie charts
    slice_field = "x"
    slice_type = "nominal"
    value_field = "y"
    value_type = "quantitative"
    aggregate_function = "count"
    title = ""
    
    # If form was submitted, get the chart parameters
    if request.method == "POST":
        slice_field = request.form.get("slice_field", slice_field)
        slice_type = request.form.get("slice_type", slice_type)
        value_field = request.form.get("value_field", value_field)
        value_type = request.form.get("value_type", value_type)
        aggregate_function = request.form.get("aggregate_function", aggregate_function)
        title = request.form.get("title", title)
    
    # Create the chart
    chart = create_pie_chart(
        slice_field=slice_field,
        slice_type=slice_type,
        value_field=value_field,
        value_type=value_type,
        aggregate_function=aggregate_function,
        title=title
    )
    
    # Generate chart spec
    chart_spec = chart.to_dict()
    chart_json = json.dumps(chart_spec)
    
    # Render the template with only the form fields needed for pie charts
    return render_template(
        "pie_chart.html",
        chart_types=CHART_TYPES,
        data_types=DATA_TYPES,
        aggregate_functions=AGGREGATE_FUNCTIONS,
        available_fields=available_fields,
        chart_json=chart_json,
        selected_chart_type="pie",
        selected_slice_field=slice_field,
        selected_slice_type=slice_type,
        selected_value_field=value_field,
        selected_value_type=value_type,
        selected_aggregate_function=aggregate_function,
        selected_title=title
    )


def handle_histogram_request(available_fields, request):
    """Handle histogram requests."""
    # Default chart parameters for histograms
    x_field = "x"
    x_type = "quantitative"
    color_field = ""
    color_type = "nominal"
    aggregate_function = "count"
    bin_step = 10
    title = ""
    
    # If form was submitted, get the chart parameters
    if request.method == "POST":
        x_field = request.form.get("x_field", x_field)
        x_type = request.form.get("x_type", x_type)
        color_field = request.form.get("color_field", color_field)
        color_type = request.form.get("color_type", color_type)
        aggregate_function = request.form.get("aggregate_function", aggregate_function)
        bin_step_str = request.form.get("bin_step", str(bin_step))
        try:
            bin_step = float(bin_step_str)
        except ValueError:
            bin_step = 10  # Default if invalid input
        title = request.form.get("title", title)
    
    # Create the chart
    chart = create_histogram(
        x_field=x_field,
        x_type=x_type,
        color_field=color_field if color_field else None,
        color_type=color_type,
        aggregate_function=aggregate_function,
        bin_step=bin_step,
        title=title
    )
    
    # Generate chart spec
    chart_spec = chart.to_dict()
    chart_json = json.dumps(chart_spec)
    
    # Render the template with only the form fields needed for histograms
    return render_template(
        "histogram.html",
        chart_types=CHART_TYPES,
        data_types=DATA_TYPES,
        aggregate_functions=AGGREGATE_FUNCTIONS,
        available_fields=available_fields,
        chart_json=chart_json,
        selected_chart_type="histogram",
        selected_x_field=x_field,
        selected_x_type=x_type,
        selected_color_field=color_field,
        selected_color_type=color_type,
        selected_aggregate_function=aggregate_function,
        selected_bin_step=bin_step,
        selected_title=title
    )


@app.route("/api/data.json")
def get_data():
    """Return the dataframe as JSON for the chart."""
    df = generate_sample_dataframe()
    return df.to_json(orient='records')


if __name__ == "__main__":
    app.run(debug=True)