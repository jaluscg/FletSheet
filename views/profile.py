import flet as ft
from flet import *
from user_controls.side_bar import SideBar


class ProfileView:
    def __init__(self):
        ...

    def view(self,page:ft.page):
       

        page_sidebar = SideBar(page,
                                lambda _: page.go('/profile'),
                                lambda _: page.go('/bar1'),
                                lambda _: page.go('/bar11'),
                                lambda _: page.go('/bar111'),
                                lambda _: page.go('/bar1111'),
                                lambda _: page.go('/bar11111'),
                                lambda _: page.go('/settings'),
                                lambda _: page.window_destroy())
        

        return ft.View(
            "/profile",
            controls=[

                        Row([
                            page_sidebar,
                            Column([
                                 TextButton(text="¿No tienes cuenta? Registrate", icon= icons.APP_REGISTRATION_SHARP, on_click=lambda _: page.go("/register")),
                                TextButton(text="¿Ya tienes cuenta? Inicia sesión", icon= icons.LOGIN_OUTLINED, on_click=lambda _: page.go("/login")),
                                
                            ], expand= True),

                        ], expand=True
                            
                            

                        )

                     
                    
            ],

            vertical_alignment =  MainAxisAlignment.CENTER, 
            horizontal_alignment = CrossAxisAlignment.CENTER, 
          
        )
