import flet as ft
from flet import *
from flet_route import Params,Basket
from user_controls.side_bar import SideBar
from user_controls.app_bar import AppBar
from user_controls.table import TextFieldTable


class MenuView:
    def __init__(self):
        ...
        self.table = TextFieldTable(22,16) #número de filas y columnas



    def view(self,page:ft.page,params:Params,basket:Basket):
        print(params)
        print(basket)

        page_sidebar = SideBar(page,
                                lambda _: page.go('/profile'),
                                lambda _: page.go('/bar1'),
                                lambda _: page.go('/bar11'),
                                lambda _: page.go('/bar111'),
                                lambda _: page.go('/bar1111'),
                                lambda _: page.go('/bar11111'),
                                lambda _: page.go('/settings'),
                                lambda _: page.window_destroy())

        table = self.table.create_table(page)

        return ft.View(
            "/menu1",
            controls=[

                        Column([
                            page_sidebar,
                            Column( [ 
                                table 
                            ],  expand= True),

                        ], expand=True
                            
                            

                        )

                     
                    
            ],

            vertical_alignment =  MainAxisAlignment.CENTER, 
            horizontal_alignment = CrossAxisAlignment.CENTER, 
          
        )