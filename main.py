import flet as ft
from flet_route import Routing
from routes import app_routes
import sys
import logging

# Configurar logging para escribir en un archivo
logging.basicConfig(filename='out.log', level=logging.DEBUG, filemode='w')



def main(page: ft.Page):
    try:
        Routing(
            page=page,
            app_routes=app_routes,
        )
        page.go(page.route)
        
    except Exception as e:
        print("Ocurrió un error:", e)
        sys.exit(100)  # Magic code para mostrar el log



ft.app(main)
    # En un entorno de desarrollo
#ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=8550)