import flet as ft
from flet import *
import re
from .funciones import evaluate_formula
import openpyxl
import sys 
import os
from .for_specific_table.SpecificColumn import SpecificColumn
from .for_specific_table.SpecificRow import SpecificRow
from .for_specific_table.SpecificScrollablecontrol import SpecificScrollableControl




class TextFieldTable():
    """
    Una matriz de celdas que se puede editar y desplazar.
    """
    def __init__(
        self,
        rows,
        cols,
        cell_height: OptionalNumber = 30,
        cell_width: OptionalNumber = 100,
        
    ):
        
        
        self.ROWS = rows
        self.COLS = cols
        self.selected_cells = [] #inicializar como lista vacía
        self.cells =  [[None for _ in range(self.COLS)] for _ in range(self.ROWS)]  # Matriz de celdas
        self.dragging = False
        self.double_clicked = False
        self.current_selected_cell = None
        self.editing_cell = None
        self.clipboard = [] #contenido copiado o cortado puede ser una lista
        self.double_clicked = False
        self.visible_start_row = 1
        self.visible_end_row =  rows
        self.visible_start_col = 1
        self.visible_end_col = cols
        self.start_cell = None 
        self.table_rows = []
        self.table_initialized = False  # Inicializa el estado de la tabla
        self.cell_height = cell_height  
        self.cell_width = cell_width
        self.btn_hoja = False
        self.edited_cells = {}  
        self.undo_stack = []  # Pila para deshacer cambios
        excel_file_path = self.get_asset_path("assets/contabilizacion.xlsx")
        self.excel_data = self.load_excel_data(excel_file_path)
        self.current_sheet = next(iter(self.excel_data), None) 

    def on_horizontal_slider_change(self, e, page):
        # Calcula el desplazamiento en las columnas basado en el valor del slider
        self.visible_start_col = int(e.control.value)
        self.visible_end_col = self.visible_end_col
        self.update_visible_cells()
        self.update_indices()
        page.update()


    def on_vertical_slider_change(self, e, page):
        # Calcula el desplazamiento en las filas basado en el valor del slider
        self.visible_start_row = int(e.control.value)
        self.visible_end_row = self.visible_end_row
        self.update_visible_cells()
        self.update_indices()
        page.update()

    def create_table(self, page):
        page.on_keyboard_event = lambda e: self.on_keyboard_event(e, page)


        container_style = {
            'border': ft.border.all(0.3, ft.colors.GREEN_500),
            'border_radius': 0.2,
            'height': self.cell_height,
            'width': self.cell_width,
        }

        
        #crear los indices de las celdas
        column_indices, row_indices = self.create_indices(page)

        
        #crear filas y columnas para la tabla usando bucles
        sheet_name = self.current_sheet
        self.table_rows= []
        for r in range(self.ROWS):
            row_cells = []
            for c in range(self.COLS):
                
                cell_content = ""
                # Inicializar con datos visibles
                if r < self.visible_end_row and c < self.visible_end_col:
                    cell_content = str(self.excel_data[sheet_name][r][c]) if r < len(self.excel_data[sheet_name]) and c < len(self.excel_data[sheet_name][r]) else ""
                
               
                custom_container_style = container_style.copy()
                custom_container_style['bgcolor'] = "#FFFFFF" if r % 2 == 0 else "#EEEEEE"
                
                tf = ft.Container(**custom_container_style, content=ft.Text(cell_content)) 


                tf.row, tf.col = r, c
                tf.formula = None #Añadirle atributo a la formula
                self.cells[r][c] = tf

                gd = ft.GestureDetector(
                    mouse_cursor=ft.MouseCursor.MOVE,
                    #on_pan_start=lambda e: None if self.is_mobile_device(page) or self.is_packege_device(page) else self.on_pan_start(e, page),
                    #on_pan_update=lambda e: None if self.is_mobile_device(page) or self.is_packege_device(page) else self.on_pan_update(e, page),
                    #on_pan_end=lambda e: None if self.is_mobile_device(page) or self.is_packege_device(page) else self.on_pan_end(e, page),
                    on_tap=lambda e: self.on_single_click(e, page),
                    on_double_tap=lambda e: self.on_double_click(e, page),
                )

                gd.row, gd.col = r, c
                
                # Aquí está el Stack
                stacked_cell = ft.Stack(
                    [
                        tf,  # TextField en la parte inferior
                        gd   # GestureDetector en la parte superior
                    ],
                    width=self.cell_width,
                    height=self.cell_height
                )
                
                row_cells.append(stacked_cell)  # Añadir el Stack en lugar del GestureDetector

             
            #añadir nueva fila a la lista de filas
            self.table_rows.append(ft.Row(row_cells, spacing=0))
        
        inicio_tabla = Column(self.table_rows, spacing=0)

        # Crear una columna con todas las filas para permitir desplazamiento vertical
        #vertical_scroll = SpecificColumn([column_indices, inicio_tabla],  spacing=0, scroll=ft.ScrollMode.ALWAYS, height=page.height /3)
        vertical_scroll = SpecificColumn([inicio_tabla],  spacing=0, scroll=ft.ScrollMode.ALWAYS, on_scroll= self.handle_vertical_scroll_event, height=page.height /3)

        # Envolver la columna en un contenedor Row para desplazamiento horizontal
        #scrollable_columns = SpecificRow([row_indices, vertical_scroll], spacing=0, scroll=ft.ScrollMode.ALWAYS,alignment=MainAxisAlignment.START, vertical_alignment=CrossAxisAlignment.START,width= page.width / 2 )
        scrollable_columns = SpecificRow([vertical_scroll], spacing=0, scroll=ft.ScrollMode.ALWAYS,alignment=MainAxisAlignment.START, on_scroll=self.handle_horizontal_scroll_event, vertical_alignment=CrossAxisAlignment.START,width= page.width / 2 )

        seccion_hojas = self.create_sheets_section(page)

        final_table = ft.Column([
                scrollable_columns,           
                seccion_hojas,
                
        ])
        

        return final_table