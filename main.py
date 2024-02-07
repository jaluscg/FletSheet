from flet import ft
from views.menu import MenuView


def main(page: ft.Page):
    page.window_title = "excel con fletsheet"
    page.horizontal_alignment = 'center'
    page.padding = 0

    def route_change(route):
        page.views.clear()
        page.views.append(
            ft.View(
                "/",
                [
                    ft.AppBar(title=ft.Text("Fletsheet"), bgcolor=ft.colors.SURFACE_VARIANT),
                    ft.ElevatedButton("Ir a tablas", on_click=lambda _: page.go("/menu")),
                ],
            )
        )

        if page.route == "/menu":
            page.views.append(
                MenuView().View
            )
        page.update()

    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go(page.route)




ft.app(main, assets_dir= 'assets/')

#ft.app(main, view=ft.AppView.WEB_BROWSER)
