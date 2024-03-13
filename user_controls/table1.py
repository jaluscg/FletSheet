import flet as ft
from flet import *
import re
from fletsheet_formula import Formulas
import openpyxl
import sys 
import os
import random
import datetime


class TextFieldTable():
    """
    Una matriz de celdas que se puede editar y desplazar.
    """

    def __init__(self, 
                excel_file_path,
                page_width, 
                page_height,
                cell_height: OptionalNumber = 30,
                cell_width: OptionalNumber = 100,
                ):
        
        self.page_width = page_width
        self.page_height = page_height
        self.ROWS = int((page_height / 30)*0.8)
        self.COLS = int((page_width / 100)*0.9)
        self.selected_cells = [] #inicializar como lista vacía
        self.cells =  [[None for _ in range(self.COLS)] for _ in range(self.ROWS)]  # Matriz de celdas
        self.dragging = False
        self.double_clicked = False
        self.current_selected_cell = None
        self.editing_cell = None
        self.clipboard = [] #contenido copiado o cortado puede ser una lista
        self.double_clicked = False
        self.visible_start_row = 1
        self.visible_end_row =  self.ROWS
        self.visible_start_col = 1
        self.visible_end_col = self.COLS
        self.start_cell = None 
        self.table_rows = []
        self.table_initialized = False  # Inicializa el estado de la tabla
        self.cell_height = cell_height  
        self.cell_width = cell_width
        self.btn_hoja = False
        self.edited_cells = {}  
        self.undo_stack = []  # Pila para deshacer cambios
        self.excel_file_path = excel_file_path
        self.excel_data = self.load_excel_data(self.excel_file_path)
        self.current_sheet = next(iter(self.excel_data), None)
        self.text_size = 14
        self.is_writing_formula = False
        self.cell_colors = {}  # Diccionario para almacenar los colores de las celdas
        self.formula_container = None
        self.container_row = None
        self.container_col = None

 
    def load_excel_data(self, filepath):
        print("se está cargando data excel")
        workbook = openpyxl.load_workbook(filepath, data_only=False)  # Cambiar data_only a False
        data = {}

        for sheet_name in workbook.sheetnames:
            worksheet = workbook[sheet_name]
            sheet_data = []
            for row in worksheet.iter_rows():
                row_data = []
                for cell in row:
                    if cell.data_type == 'f':  # Verificar si la celda contiene una fórmula
                        cell_value = cell.value  # Preceder la fórmula con '='
                    else:
                        cell_value = cell.value  # Obtener el valor de la celda como es
                    row_data.append(cell_value)
                sheet_data.append(row_data)
            data[sheet_name] = sheet_data

        return data

    def handle_scroll_event(self, e, page):
        # Calcular los índices de fila y columna basándose en el desplazamiento del scroll
        self.dragging = False

        delta_rows = int(e.scroll_delta_y / self.cell_height)
        delta_cols = int(e.scroll_delta_x / self.cell_width)

        self.visible_start_row = max(1, self.visible_start_row + delta_rows)
        self.visible_end_row = min(self.ROWS, self.visible_start_row + 12)
        
        self.visible_start_col = max(1, self.visible_start_col + delta_cols)
        self.visible_end_col = min(self.COLS, self.visible_start_col + 10)



        # Actualizar celdas visibles
        self.update_visible_cells()
        self.update_indices()


        # Actualizar la página para reflejar los cambios
        page.update()

        
    def update_visible_cells(self):
        # Verificar si se está utilizando btn_hoja y configurar el nombre de la hoja
        sheet_name = self.current_sheet if not self.btn_hoja else self.current_sheet

        if sheet_name not in self.edited_cells:
            self.edited_cells[sheet_name] = {}

        for r in range(self.ROWS):
            for c in range(self.COLS):
                # Calcular la posición real de la celda en los datos
                data_row = r + self.visible_start_row - 1
                data_col = c + self.visible_start_col - 1

                # Comprobar si la celda ha sido editada
                if (data_row, data_col) in self.edited_cells[sheet_name]:
                    cell_value = self.edited_cells[sheet_name][(data_row, data_col)]
                else:
                    # Si no ha sido editada, usar el valor de la hoja de cálculo
                    if sheet_name in self.excel_data and \
                    data_row < len(self.excel_data[sheet_name]) and \
                    data_col < len(self.excel_data[sheet_name][data_row]):
                        cell_value = self.excel_data[sheet_name][data_row][data_col]
                        if cell_value is None:
                            cell_value = ""
                    else:
                        cell_value = ""

                # Comprobar si la celda contiene una fórmula
                if isinstance(cell_value, str) and cell_value.startswith("="):
                    # Evaluar la fórmula y actualizar el valor de la celda
                    try:
                        evaluated_value = Formulas().evaluate_formula(self.cells, cell_value, data_row, data_col, "withcell")
                        cell_display_value = str(evaluated_value)
                    except Exception as e:
                        cell_display_value = "Error"
                else:
                    # Si no es una fórmula, mostrar el valor como está
                    cell_display_value = str(cell_value) if cell_value != "" else ""

                # Actualizar el valor de la celda en la interfaz de usuario
                self.cells[r][c].content.value = cell_display_value
    
    def create_table(self, page):
        page.on_keyboard_event = lambda e: self.on_keyboard_event(e, page)
        self.create_formula_container(page)  # Inicializar el contenedor de fórmulas


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
                cell_value = self.excel_data[sheet_name][r][c] if r < len(self.excel_data[sheet_name]) and c < len(self.excel_data[sheet_name][r]) else ""
                cell_content = ""                
                
                # Verificar si la celda tiene una fórmula y calcularla
                if isinstance(cell_value, str) and cell_value.startswith('='):
                    cell_content = str(Formulas().evaluate_formula(self.cells, cell_value, r, c, "withexceldata", self.excel_data[sheet_name]))
                
                elif cell_value:
                    try:
                        # Intenta formatear como fecha
                        cell_content = self.format_date(cell_value)
                    except ValueError:
                        # Si no es una fecha, mantiene el valor original
                        cell_content = cell_value
                    
                
               
                custom_container_style = container_style.copy()
                custom_container_style['bgcolor'] = "#FFFFFF" if r % 2 == 0 else "#EEEEEE"
                
                tf = ft.Container(**custom_container_style, content=ft.Text(cell_content, size=self.text_size)) 


                tf.row, tf.col = r, c
                tf.formula = cell_value
                self.cells[r][c] = tf

                gd = ft.GestureDetector(
                    mouse_cursor=ft.MouseCursor.MOVE,
                    #on_pan_start=lambda e: None if self.is_mobile_device(page) or self.is_packege_device(page) else self.on_pan_start(e, page),
                    #on_pan_update=lambda e: None if self.is_mobile_device(page) or self.is_packege_device(page) else self.on_pan_update(e, page),
                    #on_pan_end=lambda e: None if self.is_mobile_device(page) or self.is_packege_device(page) else self.on_pan_end(e, page),
                    on_tap=lambda e: self.on_single_click(e, page),
                    on_double_tap=lambda e: self.on_double_click(e, page),
                    on_scroll= lambda e: self.handle_scroll_event(e, page),
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
        
        
        # Crear una columna con todas las filas para permitir desplazamiento vertical
        table_column = ft.Column(self.table_rows,  spacing=0, scroll=ft.ScrollMode.ALWAYS)

        # Envolver la columna en un contenedor Row para desplazamiento horizontal
        scrollable_columns = ft.Row([row_indices, table_column], spacing=0)

        # Configurar el evento de scroll en el contenedor que quieres que sea desplazable

        #scrollable_columns.on_scroll = self.handle_scroll_event

        #indices de filas
        tabla_indices = ft.Column(
            [column_indices, scrollable_columns],
            spacing=0,
            width= page.width * 0.90 ,
        )

        seccion_hojas = self.create_sheets_section(page)
        vertical_slider = self.vertical_slider(page)
        horizontal_slider = self.horizontal_slider(page)

        final_table = ft.Column([
            ft.Row([
                tabla_indices,
                vertical_slider
            ],
                spacing=0,
                height= page.height * 0.70,
                scroll=ft.ScrollMode.HIDDEN),
            ft.Row([
                seccion_hojas,
            ],
                spacing=0,
                height= page.height *0.05),
            ft.Row([
                horizontal_slider
            ],  
                spacing=0,
                height= page.height *0.05)
           
        ],
        spacing=0.6,
        scroll=ft.ScrollMode.HIDDEN,
        expand=True)
        

        final_layout = ft.Column([
            self.formula_container,  # Añadir el contenedor de fórmulas en la parte superior
            final_table  
        ],
        spacing=0.7)
        return final_layout