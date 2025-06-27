"""
ColorChecker 
---------------------
An interactive Dash app to visualize ColorChecker color targets across different color spaces and versions.

Features:
- Adjustable figure size based on screen resolution
- Adjustable color square size
- Toggle RGB label display
- Dropdown controls for version and color space
- It requires excel data (ColorChecker_RGB_and_spectra.xlsx) from https://babelcolor.com/colorchecker-2.htm#CCP2_data

Author: Taehwang Son
Updated 2025. 07. 27.
"""


import pandas as pd
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output
from screeninfo import get_monitors
import os

# Get screen dimensions
monitor = get_monitors()[0]
screen_width = monitor.width
screen_height = monitor.height

# Load Excel data
excel_file = "ColorChecker_RGB_and_spectra.xlsx"
if not os.path.exists(excel_file):
    raise FileNotFoundError(f"Excel file '{excel_file}' not found. Please place it in the project directory.")
df = pd.read_excel(excel_file, sheet_name='RGB_8_bit', header=None)

# Extract ColorChecker Versions
version_row_indices = [1, 30, 59]  # A2, A31, A60 (zero-based)
colorchecker_versions = [df.iloc[row, 0] for row in version_row_indices]

# Extract Color Spaces (I2, L2, O2, ..., BK2)
col_start_indices = [8 + i * 3 for i in range(19)]  # Columns I, L, O, ..., BK (3-column spacing)
color_spaces = [df.iloc[1, col] for col in col_start_indices]

# Build Data Dictionary: data[version][color_space] = 24×3 RGB numpy array
data = {}
for version, start_row in zip(colorchecker_versions, [5, 34, 63]):
    data[version] = {}
    for cs_idx, color_space in enumerate(color_spaces):
        col_base = 8 + cs_idx * 3
        rgb_values = df.iloc[start_row-1:start_row-1+24, col_base:col_base+3].to_numpy()
        data[version][color_space] = rgb_values

# Grid positions (same for all)
n_rows, n_cols = 4, 6
x, y = [], []
for i in range(24):
    row = n_rows - 1 - (i // n_cols)
    col = i % n_cols
    x.append(col)
    y.append(row)

# Helper functions
def get_colors(version, color_space):
    rgb_array = data[version][color_space]
    return [f'rgb({r},{g},{b})' for r, g, b in rgb_array]

def get_text_labels(version, color_space):
    rgb_array = data[version][color_space]
    return [f'{int(r)} {int(g)} {int(b)}' for r, g, b in rgb_array]

def create_figure(version, color_space, selected_ratio, show_labels, selected_square_ratio):
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=x,
        y=y,
        mode='markers+text' if show_labels else 'markers',
        marker=dict(
            size=selected_square_ratio*400,
            symbol='square',
            color=get_colors(version, color_space),
        ),
        text=get_text_labels(version, color_space) if show_labels else None,
        textposition='middle center',
        textfont=dict(color='white', size=15),
        hoverinfo='none'
    ))

    fig.update_layout(
        width=int(screen_width * selected_ratio),
        height=int(screen_height * selected_ratio),
        plot_bgcolor='black',
        paper_bgcolor='black',
        xaxis=dict(visible=False, range=[-0.5, n_cols - 0.5], scaleanchor='y', scaleratio=1),
        yaxis=dict(visible=False, range=[-0.5, n_rows - 0.5]),
        margin=dict(l=0, r=0, t=0, b=0),
        showlegend=False,
    )

    return fig

# Initialize Dash App
app = Dash(__name__)

app.layout = html.Div([
    html.Div([
        html.Label('ColorChecker Version:', style={'fontFamily': 'Arial', 'color': 'white'}),
        dcc.Dropdown(
            id='version-dropdown',
            options=[{'label': v, 'value': v} for v in colorchecker_versions],
            value=colorchecker_versions[0],
            style={'fontFamily': 'Arial'}
        ),
    ], style={'width': '10%', 'display': 'inline-block', 'padding': '10px'}),

    html.Div([
        html.Label('Color Space:', style={'fontFamily': 'Arial', 'color': 'white'}),
        dcc.Dropdown(
            id='color-space-dropdown',
            options=[{'label': cs, 'value': cs} for cs in color_spaces],
            value=color_spaces[0],
            style={'fontFamily': 'Arial'}
        ),
    ], style={'width': '10%', 'display': 'inline-block', 'padding': '10px'}),

    html.Div([
        html.Label('Screen Size Ratio:', style={'fontFamily': 'Arial', 'color': 'white'}),
        dcc.Dropdown(
            id='screen-ratio-dropdown',
            options=[
                {'label': '10%', 'value': 0.1},
                {'label': '20%', 'value': 0.2},
                {'label': '30%', 'value': 0.3},
                {'label': '40%', 'value': 0.4},
                {'label': '50%', 'value': 0.5},
                {'label': '60%', 'value': 0.6},
                {'label': '70%', 'value': 0.7},
                {'label': '80%', 'value': 0.8},
                {'label': '90%', 'value': 0.9},
                {'label': '100%', 'value': 1.0},
            ],
            value=0.6,
            style={'fontFamily': 'Arial'}
        ),
    ], style={'width': '10%', 'display': 'inline-block', 'padding': '10px'}),

    html.Div([
        html.Label('Color Square ratio:', style={'fontFamily': 'Arial', 'color': 'white'}),
        dcc.Dropdown(
            id='color-square-size-dropdown',
            options=[
                {'label': '10%', 'value': 0.1},
                {'label': '20%', 'value': 0.2},
                {'label': '30%', 'value': 0.3},
                {'label': '40%', 'value': 0.4},
                {'label': '50%', 'value': 0.5},
                {'label': '60%', 'value': 0.6},
                {'label': '70%', 'value': 0.7},
                {'label': '80%', 'value': 0.8},
                {'label': '90%', 'value': 0.9},
                {'label': '100%', 'value': 1.0},
            ],
            value=0.5,
            style={'fontFamily': 'Arial'}
        ),
    ], style={'width': '10%', 'display': 'inline-block', 'padding': '10px'}),

    html.Div([
        html.Label('Show RGB Labels:', style={'fontFamily': 'Arial', 'color': 'black'}),
        dcc.RadioItems(
            id='show-labels-radio',
            options=[
                {'label': 'Show RGB value', 'value': True},
                {'label': 'Hide RGB value', 'value': False},
            ],
            value=True,
            labelStyle={'display': 'inline-block', 'marginRight': '15px', 'fontFamily': 'Arial', 'color': 'white'}

        ),
    ], style={'width': '15%', 'display': 'inline-block', 'padding': '10px', 'verticalAlign': 'middle'}),

    dcc.Graph(id='color-checker-plot')
], style={'backgroundColor': 'black', 'padding': '10px'})

@app.callback(
    Output('color-checker-plot', 'figure'),
    Input('version-dropdown', 'value'),
    Input('color-space-dropdown', 'value'),
    Input('screen-ratio-dropdown', 'value'),
    Input('show-labels-radio', 'value'),
    Input('color-square-size-dropdown', 'value')
)
def update_figure(selected_version, selected_color_space, selected_screen_ratio, selected_color_square_ratio, show_labels):
    return create_figure(selected_version, selected_color_space, selected_screen_ratio, selected_color_square_ratio, show_labels)


if __name__ == '__main__':
    app.run(debug=True)
