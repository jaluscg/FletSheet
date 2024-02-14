import flet as ft
from flet import *
from user_controls.table import TextFieldTable
import sys
import os


class MenuView:
    def __init__(self):
        ...


    def view(self,page:ft.page):
        
        
        excel_file_path = self.get_asset_path("assets/contabilizacion.xlsx")


        self.table = TextFieldTable(excel_file_path, page.width, page.height)

        table = self.table.create_table(page)

        #page.on_resize = self.on_page_resize

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
        
    
    def get_asset_path(self, relative_path):
        """
        Devuelve la ruta absoluta de un archivo, tanto en el entorno de desarrollo como en el empaquetado.
        """
        if getattr(sys, 'frozen', False):
            # Ruta para el entorno empaquetado
            base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        else:
            # Ruta para el entorno de desarrollo
            return os.path.join("./", relative_path)

        return os.path.join(base_path, relative_path)