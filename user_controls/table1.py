import flet as ft
from flet import *
import re
from .funciones import evaluate_formula
import openpyxl
import sys 
import os


class TextFieldTable():
    """
    Una matriz de celdas que se puede editar y desplazar.
    """

    def __init__(self, 
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



 
    
    def load_excel_data(self, filepath):
        workbook = openpyxl.load_workbook(filepath, data_only=True)
        formula_workbook = openpyxl.load_workbook(filepath, data_only=False)  # Cargar sin evaluar fórmulas
        data = {}
        for sheet in workbook.sheetnames:
            worksheet = workbook[sheet]
            formula_sheet = formula_workbook[sheet]
            sheet_data = []
            for row, formula_row in zip(worksheet.iter_rows(), formula_sheet.iter_rows()):
                row_data = []
                for cell, formula_cell in zip(row, formula_row):
                    # Guardar el valor o la fórmula
                    if cell.value is None and formula_cell.has_formula():
                        row_data.append("=" + formula_cell.formula)
                    else:
                        row_data.append(cell.value)
                sheet_data.append(row_data)
            data[sheet] = sheet_data
        return data
    
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
                cell_value = self.excel_data[sheet_name][r][c] if r < len(self.excel_data[sheet_name]) and c < len(self.excel_data[sheet_name][r]) else ""
                cell_content = ""
                # Verificar si la celda tiene una fórmula o un valor y asignar adecuadamente
                if cell_value is not None:
                    cell_content = str(cell_value)
                elif hasattr(cell_value, 'has_formula') and cell_value.has_formula():
                    # Aquí asumimos que hay un método has_formula en el objeto cell_value
                    cell_content = "=" + cell_value.formula
               
                custom_container_style = container_style.copy()
                custom_container_style['bgcolor'] = "#FFFFFF" if r % 2 == 0 else "#EEEEEE"
                
                tf = ft.Container(**custom_container_style, content=ft.Text(cell_content)) 


                tf.row, tf.col = r, c
                tf.formula = None #Añadirle atributo a la formula
                self.cells[r][c] = tf

                gd = ft.GestureDetector(
                    mouse_cursor=ft.MouseCursor.MOVE,
                    on_pan_start=lambda e: None if self.is_mobile_device(page) or self.is_packege_device(page) else self.on_pan_start(e, page),
                    on_pan_update=lambda e: None if self.is_mobile_device(page) or self.is_packege_device(page) else self.on_pan_update(e, page),
                    on_pan_end=lambda e: None if self.is_mobile_device(page) or self.is_packege_device(page) else self.on_pan_end(e, page),
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
        table_column = ft.Column(self.table_rows,  spacing=0)#, scroll=ft.ScrollMode.ALWAYS)

        # Envolver la columna en un contenedor Row para desplazamiento horizontal
        scrollable_columns = ft.Row([row_indices, table_column], spacing=0)

        # Configurar el evento de scroll en el contenedor que quieres que sea desplazable

        scrollable_columns.on_scroll = self.handle_scroll_event

        #indices de filas
        tabla_indices = ft.Column(
            [column_indices, scrollable_columns],
            spacing=0,
        )

       

        seccion_hojas = self.create_sheets_section(page)
        vertical_slider = self.vertical_slider(page)
        horizontal_slider = self.horizontal_slider(page)

        final_table = ft.Column([
            ft.Row([
                tabla_indices,
                vertical_slider
            ]),
            ft.Row([
                seccion_hojas,
                horizontal_slider
            ])
           
        ])
        

        return final_table



def update_visible_cells(self):
        # Verificar si se está utilizando btn_hoja y configurar el nombre de la hoja
        sheet_name = self.current_sheet if not self.btn_hoja else self.current_sheet

        if sheet_name not in self.edited_cells:
            self.edited_cells[sheet_name] = {}

        for r in range(self.ROWS):
            for c in range(self.COLS):
                # Calcular la posición real de la celda en los datos
                data_row = r + self.visible_start_row
                data_col = c + self.visible_start_col

                # Comprobar si la celda ha sido editada
                if (data_row, data_col) in self.edited_cells[sheet_name]:
                    # Si la celda ha sido editada, usar el valor editado
                    cell_value = self.edited_cells[sheet_name][(data_row, data_col)]
                else:
                    # Si no ha sido editada, usar el valor de la hoja de cálculo
                    if sheet_name in self.excel_data and \
                    data_row < len(self.excel_data[sheet_name]) and \
                    data_col < len(self.excel_data[sheet_name][data_row]):
                        cell_value = self.excel_data[sheet_name][data_row][data_col]
                    else:
                        cell_value = ""

                # Actualizar el valor de la celda en la interfaz de usuario
                self.cells[r][c].content.value = str(cell_value)
                
