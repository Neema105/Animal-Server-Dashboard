#Neema Taghipour
# CS499 Capstone Project
# username: admin
# password: password!
from dash import Dash

from repositories.user_repository import build_user_repository
from services.auth_service import AuthService
from services.dashboard_service import DashboardService
from ui.callbacks import register_callbacks
from ui.layout import build_layout

#main ap
def create_app():
    app = Dash(__name__)

    user_repository = build_user_repository()
    auth_service = AuthService(user_repository)
    dashboard_service = DashboardService()

    initial_dataframe = dashboard_service.get_initial_dataframe()
    app.layout = build_layout(initial_dataframe, dashboard_service.data_source_label)
    register_callbacks(app, auth_service, dashboard_service)
    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True, port=8050)
