import flet as ft
from flet import *
from user_controls.table import TextFieldTable


class MenuView:
    def __init__(self):
        ...


    def view(self,page:ft.page):
        
        excel_file_path = "assets/contabilizacion.xlsx"

        self.table = TextFieldTable(15, 10, excel_file_path)

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
        