import dash
from dash import dcc, html, Input, Output, dash_table
import dash_auth
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import os

VALID_USERNAME_PASSWORD_PAIRS = {
    os.getenv("ADMIN_USER", "admin"): os.getenv("ADMIN_PW", "admin")
}

df = pd.read_excel("./data_v2.xlsx")

categorical_cols = [
    "Assigned Cluster",
    "Best Consensus ID",
    "Reference",
    "Seed Class",
    "Sample Type",
    "Prediction Type",
    "Study",
    "Year",
    "Tissue",
    "Provider",
    "Product Type",
]

# Initialize app with Bootstrap theme (FLATLY theme used here)
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])

app.server.secret_key = os.getenv("SECRET_KEY", "super-secret-key")

server = app.server

auth = dash_auth.BasicAuth(app, VALID_USERNAME_PASSWORD_PAIRS)

# 1. Header Navigation Bar
navbar = dbc.NavbarSimple(
    brand="Purity Analytics & Quality Dashboard",
    brand_href="#",
    color="primary",
    dark=True,
    className="mb-4",
)

# 2. Top Controls Panel (Card)
top_controls = dbc.Card(
    dbc.CardBody(
        [
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Label(
                                "Primary Grouping / X-Axis", className="fw-bold mb-1"
                            ),
                            dcc.Dropdown(
                                id="x-axis-selector",
                                options=[
                                    {"label": col, "value": col}
                                    for col in categorical_cols
                                ],
                                value="Assigned Cluster",
                                clearable=False,
                            ),
                        ],
                        md=6,
                    ),
                    dbc.Col(
                        [
                            html.Label(
                                "Color / Categorical Split", className="fw-bold mb-1"
                            ),
                            dcc.Dropdown(
                                id="color-selector",
                                options=[
                                    {"label": col, "value": col}
                                    for col in categorical_cols
                                ],
                                value="Seed Class",
                                clearable=False,
                            ),
                        ],
                        md=6,
                    ),
                ]
            )
        ]
    ),
    className="mb-4 shadow-sm",
)

# 3. Sidebar Filter Panel (Card)
sidebar_filters = dbc.Card(
    dbc.CardBody(
        [
            html.H5("Filter Options", className="card-title text-primary mb-3"),
            html.Label("Primary Group Items", className="fw-bold small"),
            dcc.Dropdown(id="x-item-filter", multi=True, className="mb-3"),
            html.Label("Sub-Group / Color Items", className="fw-bold small"),
            dcc.Dropdown(id="color-item-filter", multi=True, className="mb-3"),
            html.Label("Sample Type", className="fw-bold small"),
            dcc.Dropdown(
                id="sample-filter",
                options=[
                    {"label": str(s), "value": s}
                    for s in sorted(df["Sample Type"].dropna().unique())
                ],
                value=list(df["Sample Type"].dropna().unique()),
                multi=True,
                className="mb-3",
            ),
            html.Label("Study", className="fw-bold small"),
            dcc.Dropdown(
                id="study-filter",
                options=[
                    {"label": str(s), "value": s}
                    for s in sorted(df["Study"].dropna().unique())
                ],
                value=list(df["Study"].dropna().unique()),
                multi=True,
                className="mb-3",
            ),
            html.Label("Prediction Type", className="fw-bold small"),
            dcc.Dropdown(
                id="prediction-type-filter",
                options=[
                    {"label": str(s), "value": s}
                    for s in sorted(df["Prediction Type"].dropna().unique())
                ],
                value=list(df["Prediction Type"].dropna().unique()),
                multi=True,
                className="mb-3",
            ),
            html.Label(
                "Show Points (Box Plot)", className="fw-bold small d-block mb-1"
            ),
            dbc.RadioItems(
                id="points-toggle",
                options=[
                    {"label": " None", "value": False},
                    {"label": " Outliers", "value": "outliers"},
                    {"label": " All", "value": "all"},
                ],
                value="outliers",
                inline=True,
            ),
            html.Label("Color Palette", className="fw-bold small d-block mt-3 mb-1"),
            dcc.Dropdown(
                id="palette-selector",
                options=[
                    {"label": "Tableau / G10", "value": "G10"},
                    {"label": "Flatly Theme Match", "value": "Flatly"},
                    {"label": "D3 Corporate", "value": "D3"},
                    {"label": "Set 2 (Soft)", "value": "Set2"},
                    {"label": "Bold / Vibrant", "value": "Bold"},
                ],
                value="G10",
                clearable=False,
                className="mb-3",
            ),
        ]
    ),
    className="shadow-sm",
)

footer = html.Footer(
    dbc.Container(
        dbc.Row(
            [
                dbc.Col(
                    html.P(
                        [
                            html.Span(
                                "Proof of Concept",
                                className="fw-bold text-warning me-1",
                            ),
                            "— Built for analytics and demonstration purposes.",
                        ],
                        className="text-muted mb-0 small",
                    ),
                    md=8,
                    className="text-center text-md-start mb-2 mb-md-0",
                ),
                dbc.Col(
                    html.A(
                        "View Source (GitHub)",
                        href="https://github.com/atrautm1/seed-purity-dashboard.git",
                        target="_blank",  # Opens link in a new browser tab
                        className="text-decoration-none text-secondary small fw-bold",
                    ),
                    md=4,
                    className="text-center text-md-end",
                ),
            ],
            className="py-3 border-top mt-5",
        ),
        fluid=True,
    )
)

# 4. Main Visual Content Tabs (Card)
main_content = dbc.Card(
    dbc.CardBody(
        [
            dbc.Tabs(
                [
                    dbc.Tab(
                        label="Plots",
                        tab_id="tab-graphs",
                        children=[
                            dbc.Row(
                                [
                                    dbc.Col(dcc.Graph(id="box-plot-graph"), md=6),
                                    dbc.Col(dcc.Graph(id="scatter-plot-graph"), md=6),
                                ],
                                className="mt-3",
                            ),
                            html.Br(),
                            dbc.Row(
                                [
                                    dbc.Col(dcc.Graph(id="barnhart-graph"), md=6),
                                    dbc.Col(dcc.Graph(id="purity-pie-graph"), md=6),
                                ],
                                className="mt-3",
                            ),
                        ],
                    ),
                    dbc.Tab(
                        label="Summary Table",
                        tab_id="tab-table",
                        children=[
                            html.Div(
                                [
                                    html.H5(
                                        "Aggregated Metrics",
                                        className="my-3 text-secondary",
                                    ),
                                    dash_table.DataTable(
                                        id="summary-table",
                                        style_table={"overflowX": "auto"},
                                        style_header={
                                            "backgroundColor": "#2c3e50",
                                            "color": "white",
                                            "fontWeight": "bold",
                                            "textAlign": "center",
                                        },
                                        style_cell={
                                            "textAlign": "center",
                                            "padding": "10px",
                                            "fontFamily": "sans-serif",
                                        },
                                        style_data_conditional=[
                                            # Alternating row background (Zebra striping)
                                            {
                                                "if": {"row_index": "odd"},
                                                "backgroundColor": "#f8f9fa",
                                            },
                                            # Red text formatting when Pct_Above_90 is less than 85%
                                            {
                                                "if": {
                                                    "column_id": "Pct_Above_90",
                                                    "filter_query": "{Pct_Above_90} < 85",
                                                },
                                                "color": "#dc3545",  # Red text
                                                "fontWeight": "bold",
                                            },
                                        ],
                                        sort_action="native",
                                        filter_action="native",
                                    ),
                                ]
                            )
                        ],
                    ),
                ],
                id="tabs",
                active_tab="tab-graphs",
            )
        ]
    ),
    className="shadow-sm",
)

# App Layout Grid
app.layout = html.Div(
    [
        navbar,
        dbc.Container(
            [
                top_controls,
                dbc.Row([dbc.Col(sidebar_filters, md=3), dbc.Col(main_content, md=9)]),
                footer,
            ],
            fluid=True,
        ),
    ]
)


# Callbacks
@app.callback(
    [Output("x-item-filter", "options"), Output("x-item-filter", "value")],
    [Input("x-axis-selector", "value")],
)
def update_x_item_options(x_col):
    unique_vals = sorted(df[x_col].astype(str).dropna().unique())
    return [{"label": val, "value": val} for val in unique_vals], unique_vals


@app.callback(
    [Output("color-item-filter", "options"), Output("color-item-filter", "value")],
    [Input("color-selector", "value")],
)
def update_color_item_options(color_col):
    unique_vals = sorted(df[color_col].astype(str).dropna().unique())
    return [{"label": val, "value": val} for val in unique_vals], unique_vals


PALETTE_DICT = {
    "G10": px.colors.qualitative.G10,
    "Flatly": ["#18BC9C", "#3498DB", "#E74C3C", "#F39C12", "#9B59B6", "#34495E"],
    "D3": px.colors.qualitative.D3,
    "Set2": px.colors.qualitative.Set2,
    "Bold": px.colors.qualitative.Bold,
}


@app.callback(
    [
        Output("box-plot-graph", "figure"),
        Output("scatter-plot-graph", "figure"),
        Output("barnhart-graph", "figure"),  # Control Chart Scatter
        Output("purity-pie-graph", "figure"),  # Distribution Pie
        Output("summary-table", "data"),
        Output("summary-table", "columns"),
    ],
    [
        Input("x-axis-selector", "value"),
        Input("color-selector", "value"),
        Input("x-item-filter", "value"),
        Input("color-item-filter", "value"),
        Input("sample-filter", "value"),
        Input("study-filter", "value"),
        Input("points-toggle", "value"),
        Input("palette-selector", "value"),
        Input("prediction-type-filter", "value"),
    ],
)
def update_dashboard(
    x_col,
    color_col,
    selected_x_items,
    selected_color_items,
    selected_samples,
    selected_studies,
    points_mode,
    palette_name,
    selected_predictions,
):
    selected_palette = PALETTE_DICT.get(palette_name, px.colors.qualitative.G10)

    unique_categories = sorted(df[color_col].astype(str).unique())
    color_map = {
        cat: selected_palette[i % len(selected_palette)]
        for i, cat in enumerate(unique_categories)
    }

    def assign_purity_class(val):
        if pd.isna(val):
            return None
        if val >= 95:
            return "A"
        if val >= 90:
            return "B"
        if val >= 80:
            return "C"
        return "D"

    purity_colors_map = {
        "A": "#2ca02c",  # standard plotly compliant green zones compliant zones compliant zones
        "B": "#bcbd22",  # standard plotly compliant yellow zones compliant zones compliant zones
        "C": "#ff7f0e",  # standard plotly compliant orange zones compliant zones compliant zones
        "D": "#d62728",  # standard plotly compliant red zones compliant zones compliant zones
    }

    filtered_df = df[
        (df["Sample Type"].isin(selected_samples or []))
        & (df["Study"].isin(selected_studies or []))
        & (df["Prediction Type"].isin(selected_predictions or []))
    ].copy()

    filtered_df["Purity Class"] = filtered_df["Purity Index"].apply(assign_purity_class)

    filtered_df["Purity Class"] = pd.Categorical(
        filtered_df["Purity Class"],
        categories=["A", "B", "C", "D"],
        ordered=True,
    )
    filtered_df[x_col] = filtered_df[x_col].astype(str)
    filtered_df[color_col] = filtered_df[color_col].astype(str)

    filtered_df = filtered_df[
        (filtered_df[x_col].isin(selected_x_items or []))
        & (filtered_df[color_col].isin(selected_color_items or []))
    ]

    # Box Plot
    box_fig = px.box(
        filtered_df,
        x=x_col,
        y="Purity Index",
        color=color_col,
        points=points_mode,
        color_discrete_map=color_map,
        hover_data=[
            c
            for c in ["Seed Class", "Prediction Type", "Study", "Year"]
            if c in filtered_df.columns
        ],
        title=f"Purity Index by {x_col}",
    )
    box_fig.update_layout(
        template="plotly_white", boxmode="group", margin=dict(l=20, r=20, t=40, b=20)
    )

    bar_df = (
        filtered_df.groupby([x_col, color_col])["Purity Index"]
        .agg(
            Total_Count="count",
            Pass_Count=lambda x: (x >= 90).sum(),
            Pct_Pass=lambda x: (x >= 90).mean() * 100,
        )
        .reset_index()
    )

    scatter_fig = px.scatter(
        bar_df,
        x="Pct_Pass",
        y="Total_Count",
        size="Total_Count",
        color=color_col,
        hover_name=x_col,
        color_discrete_map=color_map,
        custom_data=["Pass_Count"],
        title=f"Sample Volume vs. Sample Purity by {x_col}",
        size_max=30,  # Prevents points from becoming excessively large
    )
    scatter_fig.add_vline(
        x=80,
        line_dash="dot",  # Options: "dot", "dash", "longdash", "dashdot"
        line_color="gray",  # Line color
        line_width=2,  # Line thickness
        annotation_text="Target",  # Optional label
        annotation_position="top left",
        annotation_font_color="gray",
    )
    scatter_fig.update_traces(
        hovertemplate=(
            "<b>%{hovertext}</b> (%{fullData.name})<br>"
            "Pass Rate: %{x:.1f}%<br>"
            "Total Samples: %{y}<br>"
            "# Samples ≥ 90% Purity: %{customdata[0]}<extra></extra>"
        )
    )

    scatter_fig.update_layout(
        template="plotly_white",
        xaxis_title="% of Samples ≥ 90% Purity",
        yaxis_title="Total Sample Count",
        margin=dict(l=20, r=20, t=40, b=20),
    )

    barnhart_df = filtered_df.reset_index(drop=True)

    barnhart_fig = px.strip(
        barnhart_df,
        x=x_col,
        y="Purity Index",
        color="Purity Class",
        color_discrete_map=purity_colors_map,
        hover_data=[
            c
            for c in ["Sample Type", "Study", "Prediction Type"]
            if c in barnhart_df.columns
        ],
        title="Purity Control Chart (Quality Bands)",
    )

    # Add shaded background zones for Barnhart control limits
    zones = [
        {
            "y0": 95,
            "y1": 100,
            "color": "rgba(44, 160, 44, 0.12)",
            "label": "Class A (95-100)",
        },
        {
            "y0": 90,
            "y1": 95,
            "color": "rgba(188, 189, 34, 0.12)",
            "label": "Class B (90-95)",
        },
        {
            "y0": 80,
            "y1": 90,
            "color": "rgba(255, 127, 14, 0.12)",
            "label": "Class C (80-90)",
        },
        {
            "y0": 0,
            "y1": 80,
            "color": "rgba(214, 39, 40, 0.12)",
            "label": "Class D (<80)",
        },
    ]

    for zone in zones:
        barnhart_fig.add_hrect(
            y0=zone["y0"],
            y1=zone["y1"],
            fillcolor=zone["color"],
            layer="below",
            line_width=0,
            annotation=None,
            # annotation_text=zone["label"],
            # annotation_position="top right",
            # annotation_font_size=10,
            # annotation_font_color="gray",
        )

        barnhart_fig.add_annotation(
            x=1.02,  # 2% beyond the right edge of the plot
            y=(zone["y0"] + zone["y1"]) / 2,  # Vertically centered in the zone
            xref="x domain",  # Relative to plot domain (0=left, 1=right)
            yref="y",  # Data coordinates on Y-axis
            text=f"{zone['label']}",
            showarrow=False,
            xanchor="left",  # Align text starting from x position
            yanchor="middle",
            font=dict(size=10, color="#555555"),
        )

    barnhart_fig.update_layout(
        template="plotly_white",
        yaxis=dict(range=[0, 105], title="Purity Index (%)"),
        xaxis_title=x_col,
        showlegend=False,
        margin=dict(
            l=20, r=130, t=40, b=20
        ),  # r=130 creates space on the right for labels
    )

    pie_counts = (
        filtered_df["Purity Class"]
        .value_counts()
        .reindex(["A", "B", "C", "D"], fill_value=0)
        .reset_index()
    )
    pie_counts.columns = ["Purity Class", "Count"]

    purity_pie_fig = px.pie(
        pie_counts,
        names="Purity Class",
        values="Count",
        color="Purity Class",
        color_discrete_map=purity_colors_map,
        category_orders={"Purity Class": ["A", "B", "C", "D"]},
        title="Purity Classes",
        hole=0.3,  # Converts to donut style for improved readability
    )
    purity_pie_fig.update_traces(
        textinfo="percent+label+value",
        hovertemplate="Class %{label}: <b>%{value}</b> samples (%{percent})<extra></extra>",
    )
    purity_pie_fig.update_layout(
        template="plotly_white",
        margin=dict(l=20, r=20, t=40, b=20),
    )

    # Summary Table Data
    if not filtered_df.empty:
        summary_df = (
            filtered_df.groupby([x_col, color_col])
            .agg(
                Count=("Purity Index", "count"),
                Mean=("Purity Index", "mean"),
                Std_Dev=("Purity Index", "std"),
                # Min=("Purity Index", "min"),
                # Median=("Purity Index", "median"),
                # Max=("Purity Index", "max"),
                Pct_A=("Purity Class", lambda x: (x == "A").mean() * 100),
                Pct_B=("Purity Class", lambda x: (x == "B").mean() * 100),
                Pct_C=("Purity Class", lambda x: (x == "C").mean() * 100),
                Pct_D=("Purity Class", lambda x: (x == "D").mean() * 100),
            )
            .reset_index()
            .round(2)
        )
    else:
        summary_df = pd.DataFrame(
            columns=[
                x_col,
                color_col,
                "Count",
                "Mean",
                "Std_Dev",
                # "Min",
                # "Median",
                # "Max",
                "Pct_Above_90",
            ]
        )

    table_data = summary_df.to_dict("records")

    col_map = {
        "Std_Dev": "Std Dev",
        "Pct_A": "% Class A",
        "Pct_B": "% Class B",
        "Pct_C": "% Class C",
        "Pct_D": "% Class D",
    }
    # col_map = {"Pct_Above_90": "% Above 90% Purity", "Std_Dev": "Std Dev"}
    table_columns = [
        {"name": col_map.get(i, i.replace("_", " ").title()), "id": i}
        for i in summary_df.columns
    ]

    return box_fig, scatter_fig, barnhart_fig, purity_pie_fig, table_data, table_columns


if __name__ == "__main__":
    app.run(debug=os.getenv("DEBUG", True))
