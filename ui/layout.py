import base64
import os

from dash import dcc, html, dash_table

#html layout
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
IMAGE_FILE = os.path.join(BASE_DIR, "Grazioso_Software_Logo.png")


def get_logo_src() -> str:
    try:
        with open(IMAGE_FILE, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read())
        return f"data:image/png;base64,{encoded_image.decode()}"
    except FileNotFoundError:
        print(f"Warning: Logo file '{IMAGE_FILE}' not found.")
        return ""


def build_layout(initial_dataframe, data_source_label: str):
    logo_src = get_logo_src()

    return html.Div(
        [
            dcc.Store(id="auth-ok", data=False),
            html.Center(html.B(html.H1("CS-340 Dashboard"))),
            html.Center(html.Img(src=logo_src, style={"height": "100px"})),
            html.Center(html.B("Neema Taghipour")),
            html.Center(html.Div(f"Data source: {data_source_label}", style={"marginTop": "8px"})),
            html.Hr(),
            html.Div(
                [
                    dcc.Input(id="login-user", type="text", placeholder="Username"),
                    dcc.Input(id="login-pass", type="password", placeholder="Password"),
                    html.Button("Login", id="login-button", n_clicks=0),
                    html.Div("Default login: admin / CS499Dash!", id="login-message", style={"marginTop": "10px"}),
                    html.Hr(),
                    dcc.Input(id="create-user", type="text", placeholder="New username"),
                    dcc.Input(id="create-pass", type="password", placeholder="New password"),
                    dcc.Input(id="security-question", type="text", placeholder="Security question"),
                    dcc.Input(id="security-answer", type="text", placeholder="Security answer"),
                    html.Button("Create User", id="create-button", n_clicks=0),
                    html.Div(id="create-message", style={"marginTop": "10px"}),
                    html.Hr(),
                    dcc.Input(id="forgot-user", type="text", placeholder="Username for recovery"),
                    dcc.Input(id="forgot-answer", type="text", placeholder="Security answer"),
                    dcc.Input(id="forgot-pass", type="password", placeholder="New password"),
                    html.Button("Forgot Password", id="forgot-button", n_clicks=0),
                    html.Div(id="question-message", style={"marginTop": "10px"}),
                    html.Div(id="forgot-message", style={"marginTop": "10px"}),
                ],
                id="login-box",
            ),
            html.Div(
                [
                    html.Div(
                        dcc.RadioItems(
                            id="filter-type",
                            options=[
                                {"label": "Reset", "value": "RESET"},
                                {"label": "Water Rescue", "value": "WATER"},
                                {"label": "Mountain or Wilderness Rescue", "value": "MOUNTAIN"},
                                {"label": "Disaster or Individual Tracking", "value": "DISASTER"},
                            ],
                            value="RESET",
                        )
                    ),
                    html.Hr(),
                    dash_table.DataTable(
                        id="datatable-id",
                        columns=[{"name": column, "id": column, "deletable": False, "selectable": True} for column in initial_dataframe.columns],
                        data=initial_dataframe.to_dict("records"),
                        page_size=10,
                        row_selectable="single",
                        selected_rows=[0],
                    ),
                    html.Br(),
                    html.Div(
                        [
                            html.Label("Sort column"),
                            dcc.Dropdown(
                                id="sort-column",
                                options=[{"label": column, "value": column} for column in initial_dataframe.columns],
                                value="age_upon_outcome_in_weeks",
                                clearable=False,
                            ),
                            html.Br(),
                            html.Label("Display sorted results with"),
                            dcc.RadioItems(
                                id="sort-algorithm",
                                options=[
                                    {"label": "Quick Sort", "value": "quick"},
                                    {"label": "Merge Sort", "value": "merge"},
                                    {"label": "Heap Sort", "value": "heap"},
                                    {"label": "Selection Sort", "value": "selection"},
                                    {"label": "Insertion Sort", "value": "insertion"},
                                    {"label": "Bubble Sort", "value": "bubble"},
                                ],
                                value="quick",
                                inline=False,
                            ),
                            html.Br(),
                            html.Label("Sort order"),
                            dcc.RadioItems(
                                id="sort-order",
                                options=[
                                    {"label": "Ascending", "value": "asc"},
                                    {"label": "Descending", "value": "desc"},
                                ],
                                value="asc",
                                inline=True,
                            ),
                            html.Div(id="sort-timing-output", style={"marginTop": "10px", "fontWeight": "bold"}),
                        ]
                    ),
                    html.Br(),
                    html.Hr(),
                    html.Div(
                        className="row",
                        style={"display": "flex"},
                        children=[
                            html.Div(id="graph-id", className="col s12 m6"),
                            html.Div(id="map-id", className="col s12 m6"),
                        ],
                    ),
                ],
                id="dashboard-box",
                style={"display": "none"},
            ),
        ]
    )
