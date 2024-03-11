import flet as ft
from flet import *
import re
from ..fletsheet_formula.funciones import evaluate_formula
import openpyxl
import sys 
import os
import random


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


    def on_keyboard_event(self, e:ft.KeyboardEvent, page):

        
        def parse_cell_references(formula):
            # Regular expression to find cell references like A1, B2, etc.
            pattern = r'([A-Za-z]+[0-9]+)'
            return re.findall(pattern, formula)
       
        
        def get_cell_from_reference(ref):
            # Assuming the cell references are in the format 'A1', 'B2', etc.
            # Convert column letter to column index (e.g., 'A' -> 0, 'B' -> 1)
            col = ord(ref[0].upper()) - ord('A')
            # Convert row number to row index (e.g., '1' -> 0, '2' -> 1)
            row = int(ref[1:]) - 1
            # Return the cell object at the calculated row and column
            return self.cells[row][col]

        def almacenar_datoescrito(current_row, current_col, current_cell, previous_value):
            adjusted_row = current_row - 1 + self.visible_start_row
            adjusted_col = current_col - 1 + self.visible_start_col

            sheet_name = self.current_sheet
            if sheet_name not in self.edited_cells:
                self.edited_cells[sheet_name] = {}

            # Determinar si el contenido de la celda es una fórmula o un valor
            if isinstance(current_cell.content.value, str) and current_cell.content.value.startswith('='):
                # Almacenar como fórmula
                edited_value = current_cell.content.value
            else:
                # Almacenar como valor normal
                edited_value = current_cell.content.value

            self.edited_cells[sheet_name][(adjusted_row, adjusted_col)] = edited_value

            self.undo_stack.append(('edit', sheet_name, current_row, current_col, previous_value, edited_value))
            print(f"edited_cells:{self.edited_cells}" )
           
            
            

        

        # Verificar si hay alguna celda seleccionada
        if not self.selected_cells:
            return
        
        # Utilizar la última celda seleccionada
        current_cell = self.selected_cells[-1]

        current_row = current_cell.row
        current_col = current_cell.col
        
      
        
          

        if re.match(r'^[a-zA-Z0-9\s=+\-*/()!@#$%^&*<>?{}\[\]~`|:;"\',.<>\/\^_`{|}~\\]$', e.key):
            if not e.ctrl:
                previous_value = current_cell.content.value  # Capturar el valor original

                if self.editing_cell != current_cell and not self.double_clicked:
                    current_cell.content.value = ""  # Borra el contenido existente
                    self.editing_cell = current_cell  # Actualiza el estado de edición

                current_text = current_cell.content.value #obtener texto actual del objeto Text

                # Si la tecla es alfanumérica, considera mayúsculas y minúsculas
                if re.match(r'^[a-zA-Z0-9=+\-*/()!@#$%^&*<>?{}[\]~`|]$', e.key):
                    if e.shift:
                        # Añadir una comprobación adicional para asegurar que e.key es una letra
                        if re.match(r'^[a-zA-Z]$', e.key):
                            current_cell.content.value = current_text + e.key.upper()

                        else: 
                            current_cell.content.value = current_text + e.key
                        
                    else:
                        current_cell.content.value = current_text + e.key.lower()
                else:  # Para otros caracteres como '=', '+', '-', etc.
                        current_cell.content.value = current_text + e.key
                        
                almacenar_datoescrito(current_row, current_col, current_cell, previous_value)

            page.update()
        
        
        if e.key == "=":
            self.is_writing_formula = True

        if self.is_writing_formula:
            cell_references = parse_cell_references(current_cell.content.value)
            for ref in cell_references:
                cell_to_highlight = get_cell_from_reference(ref)
                self.iluminar(cell_to_highlight, page)

        if e.key == "Enter":
        
            self.double_clicked = False 

            if not self.selected_cells:
                return

            if self.double_clicked:
                return

            if self.editing_cell:  
                if self.editing_cell.content.value.startswith("="):
                    row, col = self.editing_cell.row, self.editing_cell.col
                    formula = self.editing_cell.content.value  
                    result = evaluate_formula(self.cells, formula, row, col, "withcell") 
                    self.editing_cell.formula = formula  
                    self.editing_cell.content.value = str(result)  # Asegurarse de que el resultado se refleje en la celda
                    print(self.cell_colors)
                    self.unhighlight_cell_colors(page)


                self.editing_cell = None  
            page.update()

            return  # Finalizar el manejo del evento aquí, ya que hemos manejado la tecla "Enter"

        if e.ctrl == True:
            if e.key == "Arrow Down":
                last_row, _ = self.find_last_value_cell("down")
                if last_row:
                    self.visible_start_row = max(1, last_row - 12)
                    self.visible_end_row = min(self.ROWS, last_row + 1)
            elif e.key == "Arrow Right":
                _, last_col = self.find_last_value_cell("right")
                if last_col:
                    self.visible_start_col = max(1, last_col - 10)
                    self.visible_end_col = min(self.COLS, last_col + 1)

            # Actualiza las celdas visibles y la página
            self.update_visible_cells()
            self.update_indices()
            page.update()

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
                    cell_content = str(evaluate_formula(self.cells, cell_value, r, c, "withexceldata", self.excel_data[sheet_name] ))

                elif cell_value is not None:
                    cell_content = str(cell_value)
                
               
                custom_container_style = container_style.copy()
                custom_container_style['bgcolor'] = "#FFFFFF" if r % 2 == 0 else "#EEEEEE"
                
                tf = ft.Container(**custom_container_style, content=ft.Text(cell_content, size=self.text_size)) 


                tf.row, tf.col = r, c
                tf.formula = cell_value
                self.cells[r][c] = tf

    