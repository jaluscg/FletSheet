import flet as ft
from flet_route import Routing
from routes import app_routes
import sys
import logging
import time


# Configurar logging para escribir en un archivo
#logging.basicConfig(filename='out.log', level=logging.DEBUG, filemode='w')


def main(page: ft.Page):
    # Crear y mostrar el indicador de progreso
    progress_ring = ft.ProgressRing()
    page.add(progress_ring)

    try:
        # Pausar para simular carga (3 segundos)
        time.sleep(3)

        # Realizar las operaciones mientras se muestra el indicador de progreso
        Routing(
            page=page,
            app_routes=app_routes,
        )
        page.go(page.route)
    except Exception as e:
        print("Ocurrió un error:", e)
        sys.exit(100)  # Magic code para mostrar el log
    finally:
        # Ocultar el indicador de progreso al finalizar
        progress_ring.visible = False
        page.update()


if __name__ == "__main__":
    ft.app(target=main)

#ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=8550)