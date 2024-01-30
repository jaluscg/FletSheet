import flet as ft
from flet_route import Routing
from routes import app_routes
from middlewares.app_middleware import AppBasedMiddleware

import logging

# Configurar logging para escribir en un archivo
logging.basicConfig(filename='out.log', level=logging.DEBUG, filemode='w')


def main(page: ft.Page):

    Routing(
        page = page,
        app_routes = app_routes,
        middleware = AppBasedMiddleware().call_me
    )
    page.go(page.route)

     # Código para manejar la salida del log al finalizar
    try:
        ft.app(main)
    except SystemExit as e:
        if e.code == 100:
            with open("out.log", "r") as f:
                log = f.read()
            page.add(ft.AlertDialog(content=ft.Text(log), actions=[ft.Text("Cerrar")]))
        else:
            raise


ft.app(main)
    # En un entorno de desarrollo
#ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=8550)