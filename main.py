import flet as ft
import sys
import logging



def main(page: ft.Page):

   

    page.add(
        ft.SafeArea(
            content= ft.TextButton("Oprimir", on_click=page.go("/menu")))
            )

   


ft.app(main)

#ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=8550)