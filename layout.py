import pandas as pd
import dash_leaflet as dl
import plotly.express as px
from dash import ctx, dcc, html
from dash.dependencies import Input, Output, State

#livecallbacks

def register_callbacks(app, auth_service, dashboard_service):
    @app.callback(
        [
            Output("auth-ok", "data"),
            Output("login-message", "children"),
            Output("create-message", "children"),
            Output("question-message", "children"),
            Output("forgot-message", "children"),
        ],
        [
            Input("login-button", "n_clicks"),
            Input("create-button", "n_clicks"),
            Input("forgot-button", "n_clicks"),
        ],
        [
            State("login-user", "value"),
            State("login-pass", "value"),
            State("create-user", "value"),
            State("create-pass", "value"),
            State("security-question", "value"),
            State("security-answer", "value"),
            State("forgot-user", "value"),
            State("forgot-answer", "value"),
            State("forgot-pass", "value"),
        ],
    )
    def handle_auth(_, __, ___, entered_user, entered_pass, create_user, create_pass, security_question, security_answer, forgot_user, forgot_answer, forgot_pass):
        action = ctx.triggered_id

        if action == "create-button":
            result = auth_service.create_user(create_user, create_pass, security_question, security_answer)
        elif action == "forgot-button":
            result = auth_service.reset_password(forgot_user, forgot_answer, forgot_pass)
        else:
            result = auth_service.login(entered_user, entered_pass)

        return (
            result.auth_ok,
            result.login_message,
            result.create_message,
            result.question_message,
            result.forgot_message,
        )

    @app.callback(
        [Output("login-box", "style"), Output("dashboard-box", "style")],
        [Input("auth-ok", "data")],
    )
    def toggle_login(auth_ok):
        return ({"display": "none"}, {"display": "block"}) if auth_ok else ({}, {"display": "none"})

    @app.callback(
        [Output("datatable-id", "data"), Output("sort-timing-output", "children")],
        [
            Input("filter-type", "value"),
            Input("sort-column", "value"),
            Input("sort-algorithm", "value"),
            Input("sort-order", "value"),
        ],
    )
    def update_dashboard(filter_type, sort_column, sort_algorithm, sort_order):
        return dashboard_service.get_sorted_records(filter_type, sort_column, sort_algorithm, sort_order)

    @app.callback(Output("graph-id", "children"), [Input("datatable-id", "derived_virtual_data")])
    def update_graphs(view_data):
        if not view_data:
            return []
        dataframe = pd.DataFrame.from_dict(view_data)
        figure = px.histogram(dataframe, x="breed", title="Preferred Animals")
        return [dcc.Graph(figure=figure)]

    @app.callback(
        Output("datatable-id", "style_data_conditional"),
        [Input("datatable-id", "selected_columns")],
    )
    def update_styles(selected_columns):
        if not selected_columns:
            return []
        return [{"if": {"column_id": column_id}, "background_color": "#D2F3FF"} for column_id in selected_columns]

    @app.callback(
        Output("map-id", "children"),
        [Input("datatable-id", "derived_virtual_data"), Input("datatable-id", "derived_virtual_selected_rows")],
    )
    def update_map(view_data, selected_rows):
        if not view_data or not selected_rows:
            return []

        dataframe = pd.DataFrame.from_dict(view_data)
        row_index = selected_rows[0]

        if len(dataframe) == 0 or row_index >= len(dataframe):
            return []

        return [
            dl.Map(
                style={"width": "1000px", "height": "500px"},
                center=[30.75, -97.48],
                zoom=10,
                children=[
                    dl.TileLayer(id="base-layer-id"),
                    dl.Marker(
                        position=[dataframe.iloc[row_index]["location_lat"], dataframe.iloc[row_index]["location_long"]],
                        children=[
                            dl.Tooltip(dataframe.iloc[row_index]["breed"]),
                            dl.Popup([html.H1("Animal Name"), html.P(dataframe.iloc[row_index]["name"])]),
                        ],
                    ),
                ],
            )
        ]
