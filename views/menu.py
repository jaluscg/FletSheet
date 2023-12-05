import flet as ft
from flet import *
from flet_route import Params,Basket
from user_controls.side_bar import SideBar
from user_controls.app_bar import AppBar
from user_controls.table import TextFieldTable


class MenuView:
    def __init__(self):
        ...
        self.table = TextFieldTable(4,5) #número de filas y columnas



    def view(self,page:ft.page,params:Params,basket:Basket):
        print(params)
        print(basket)


        table = self.table.create_table(page)

        return ft.View(
            "/menu1",
            controls=[

                        Column([ 
                            Row([
                                ft.TextButton("añadir fila",  on_click=lambda e: self.table.add_row(e, page)),
                                ft.TextButton("añadir columna",  on_click=lambda e: self.table.add_col(e, page)),
                                ft.TextButton("eliminar fila",  on_click=lambda e: self.table.remove_row(e, page)),
                                ft.TextButton("eliminar columna",  on_click=lambda e: self.table.remove_col(e, page)), 
                                ]),
                            Column( [ 
                                table 
                            ],  expand= True),

                        ], expand=True
                            
                            

                        )

                     
                    
            ],

            vertical_alignment =  MainAxisAlignment.CENTER, 
            horizontal_alignment = CrossAxisAlignment.CENTER, 
          
        )