import flet as ft
from flet_route import Routing
from routes import app_routes
from middlewares.app_middleware import AppBasedMiddleware
import sys


def main(page: ft.Page):

    Routing(
        page = page,
        app_routes = app_routes,
        middleware = AppBasedMiddleware().call_me
    )
    page.go(page.route)


if getattr(sys, 'frozen', False):
    # En un entorno empaquetado
    ft.app(target=main)
else:
    # En un entorno de desarrollo
    ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=8550)