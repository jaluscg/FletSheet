import flet as ft
from flet import *

class AppBarView(UserControl):
    def __init__(self, page: ft.Page, **routes):
        self.page = page
        self.routes = routes
        super().__init__()

    def HighlightContainer(self, e):
        # Define hover effects similar to the SideBar class
        ...

    def AppBarButton(self, icon_name, route):
        return ft.IconButton(
            icon=icon_name,
            on_click=lambda _: self.page.go(route)
        )

    def build(self):
        buttons = []
        
        # Create a button for each route and its associated icon
        for route, icon in self.routes.items():
            button = self.AppBarButton(icon, route)
            buttons.append(button)

        return Container(
            height=60,  # AppBar height
            bgcolor="#272726",
            padding=10,
            content=Row(
                alignment=MainAxisAlignment.CENTER,
                controls=buttons
            ),
        )

def AppBar(page, **routes):
    app_bar = AppBarView(page, **routes)
    return app_bar.build()