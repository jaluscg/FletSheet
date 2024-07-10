import flet as ft
from flet_route import Routing
from routes import app_routes
import sys
import logging
import time



def main(page: ft.Page):
     Routing(
            page=page,
            app_routes=app_routes,
        )
     page.go(page.route)

#ft.app(main, assets_dir='assets/')

ft.app(main, view=ft.AppView.WEB_BROWSER)