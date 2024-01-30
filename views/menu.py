import flet as ft
from flet import *
from user_controls.table import TextFieldTable


class MenuView:
    def __init__(self):
        ...
        self.table = TextFieldTable(8,7) #número de filas y columnas



    def view(self,page:ft.page):
        


        table = self.table.create_table(page)

        return  ft.View(
            "/menu",
            controls=[

                ft.SafeArea(
                    content=

                        Column([ 
                            Column( [ 
                                table 
                            ],  expand= True),

                        ], expand=True
                            
                            

                        )

                     
                )     
            ],

            vertical_alignment =  MainAxisAlignment.CENTER, 
            horizontal_alignment = CrossAxisAlignment.CENTER, 
          
        )
        