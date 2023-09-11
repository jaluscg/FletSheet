import flet as ft
from flet_route import Routing
from routes import app_routes
from middlewares.app_middleware import AppBasedMiddleware
import re

def main(page: ft.Page):

    Routing(
        page = page,
        app_routes = app_routes,
        middleware = AppBasedMiddleware().call_me
    )
    page.go(page.route)

ft.app(port=8550, target=main, view=ft.AppView.WEB_BROWSER)