import flet as ft
from flet import *
from user_controls.table import TextFieldTable
import sys
import os


class MenuView:
    def __init__(self):
        ...
        self.main_stack = None
        self.table_instance = None  # Añadir una propiedad para mantener la referencia


    def view(self,page:ft.page):
        
        
        excel_file_path = self.get_asset_path("assets/contabilizacion.xlsx")
        #excel_file_path = self.get_asset_path("prueba.xlsx")


        # Guardar la instancia de TextFieldTable para usarla más tarde
        self.table_instance = TextFieldTable(excel_file_path, page.width, page.height)
        table = self.table_instance.create_table(page)


        page.on_resize = self.on_page_resize

        self.main_stack = Stack(
            controls=[
                table,
            ],
            width=page.width,
            height=page.height,
        )

        return  ft.View(
            "/menu",
            controls=[

                ft.SafeArea(
                    content=

                        Column([ 
                                self.main_stack
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
    
    def on_page_resize(self, e):
        if self.table_instance:
            self.table_instance.save_excel_data()  # Guardar los datos de la tabla si es necesario

        excel_file_path = self.get_asset_path("assets/contabilizacion.xlsx")

        # Recrear la tabla con el nuevo tamaño
        self.table_instance = TextFieldTable(excel_file_path, e.page.width, e.page.height)
        new_table = self.table_instance.create_table(e.page)

        # Actualizar el tamaño del Stack principal y otros contenedores, si es necesario
        self.main_stack.width = e.page.width
        self.main_stack.height = e.page.height
        #self.main_stack.expand = True

        # Reemplazar los controles actualizados en la vista principal
        self.main_stack.controls = [new_table]

        e.page.update()
