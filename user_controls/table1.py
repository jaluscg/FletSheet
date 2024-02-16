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

    

    def highlight_cell(self, cell, page):
        
        if cell not in self.selected_cells:
            cell.border = ft.border.all(1.5, ft.colors.PINK_400)
            self.selected_cells.append(cell)
            print(f"Resaltando celda en {cell.row}, {cell.col}")
            page.update()
            


    def unhighlight_cell(self, cell, page):

        if cell in self.selected_cells:
            cell.border = ft.border.all(0.3, ft.colors.GREEN_500)
            self.selected_cells.remove(cell)
            print(f"desresaltando celda en {cell.row}, {cell.col}")
            page.update()
            

    def clear_all_highlights(self, page):
        for cell in self.selected_cells[:]:  # Haz una copia de la lista para iterar
            self.unhighlight_cell(cell, page)
        self.selected_cells.clear()  # Limpia la lista original
        
    def on_single_click(self, e: ft.TapEvent, page):
        
        print("On single click")
    
        cell = self.cells[e.control.row][e.control.col]

        # Desresaltar todas las celdas previamente seleccionadas
        self.clear_all_highlights(page)

        # Resaltar la celda actualmente seleccionada
        self.highlight_cell(cell, page)

        # Actualizar la celda actualmente seleccionada
        self.current_selected_cell = cell

        self.table_initialized = True 
        

    def on_double_click(self, e: ft.TapEvent, page):
        self.double_clicked = True
        cell = self.cells[e.control.row][e.control.col]
        # Desresaltar todas las celdas previamente seleccionadas
        self.clear_all_highlights(page)

        # Resaltar la celda actualmente seleccionada
        self.highlight_cell(cell, page)

        # Actualizar la celda actualmente seleccionada
        self.current_selected_cell = cell

        row= e.control.row
        col = e.control.col

        self.table_initialized = True 
        
        # Crear y configurar CupertinoTextField para la edición
        text_field = CupertinoTextField(
            value=str(cell.content.value), 
            on_submit=lambda  e: self.save_edited_value(row, col, cell.content.value, page),
            autofocus=True,
            placeholder_text="",
            text_size= self.text_size,
        )

        # Actualizar el contenido de la celda para mostrar el TextField
        cell.content = text_field
        page.update()
    
    def save_edited_value(self, row, col, value, page):
        # Actualizar el valor de la celda en la estructura de datos
        self.excel_data[self.current_sheet][row][col] = value

        # Actualizar la visualización de la celda para mostrar el nuevo valor
        cell = self.cells[row][col]
        cell.content = ft.Text(value, size=self.text_size)  # Reemplazar el TextField por un Text con el nuevo valor

        self.double_clicked = False 

        
        if cell.content.value.startswith("="):
                    row, col = row, col
                    formula = cell.content.value  
                    result = evaluate_formula(self.cells, formula, row, col) 
                    cell.formula = formula  
                    cell.content.value = str(result) 

        self.editing_cell = None  

        page.update()

        
    def on_keyboard_event(self, e:ft.KeyboardEvent, page):

        def almacenar_datoescrito(current_row, current_col, current_cell, previous_value):
            adjusted_row = current_row -1 + self.visible_start_row 
            adjusted_col = current_col -1 + self.visible_start_col 

            sheet_name = self.current_sheet 
            if sheet_name not in self.edited_cells:
                self.edited_cells[sheet_name] = {}
            self.edited_cells[sheet_name][(adjusted_row, adjusted_col)] = current_cell.content.value

            self.undo_stack.append(('edit', sheet_name, current_row, current_col, previous_value, current_cell.content.value))

        # Verificar si hay alguna celda seleccionada
        if not self.selected_cells:
            return
        
        # Utilizar la última celda seleccionada
        current_cell = self.selected_cells[-1]

        current_row = current_cell.row
        current_col = current_cell.col
        
   
      
        # Primero, verifica si la tecla es alfanumérica y pone el foco en la celda
        if re.match(r'^[a-zA-Z0-9=+\-*/()!@#$%^&*<>?{}[\]~`|]$', e.key):
            if not e.ctrl:
                previous_value = current_cell.content.value  # Capturar el valor original

                if self.editing_cell != current_cell and not self.double_clicked:
                    current_cell.content.value = ""  # Borra el contenido existente
                    self.editing_cell = current_cell  # Actualiza el estado de edición

                current_text = current_cell.content.value #obtener texto actual del objeto Text

                # Si la tecla es alfanumérica, considera mayúsculas y minúsculas
                if re.match(r'^[a-zA-Z0-9]$', e.key):
                    if e.shift:
                        current_cell.content.value = current_text + e.key.upper()
                    else:
                        current_cell.content.value = current_text + e.key.lower()
                else:  # Para otros caracteres como '=', '+', '-', etc.
                        current_cell.content.value = current_text + e.key
                        
                almacenar_datoescrito(current_row, current_col, current_cell, previous_value)

            page.update()

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
                    result = evaluate_formula(self.cells, formula, row, col) 
                    self.editing_cell.formula = formula  
                    self.editing_cell.content.value = str(result)  # Asegurarse de que el resultado se refleje en la celda

                self.editing_cell = None  
            page.update()

            return  # Finalizar el manejo del evento aquí, ya que hemos manejado la tecla "Enter"
        
    def save_excel_data(self):
        workbook = openpyxl.load_workbook(self.excel_file_path)
        worksheet = workbook[self.current_sheet]
        for row_index, row in enumerate(self.excel_data[self.current_sheet]):
            for col_index, value in enumerate(row):
                if worksheet.cell(row=row_index + 1, column=col_index + 1).value != value:
                    worksheet.cell(row=row_index + 1, column=col_index + 1).value = value
        workbook.save(self.excel_file_path)
        print(f"Datos guardados exitosamente en {self.excel_file_path}")
    


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
                    #on_pan_start=lambda e: None if self.is_mobile_device(page) or self.is_packege_device(page) else self.on_pan_start(e, page),
                    #on_pan_update=lambda e: None if self.is_mobile_device(page) or self.is_packege_device(page) else self.on_pan_update(e, page),
                    #on_pan_end=lambda e: None if self.is_mobile_device(page) or self.is_packege_device(page) else self.on_pan_end(e, page),
                    on_tap=lambda e: self.on_single_click(e, page),
                    on_double_tap=lambda e: self.on_double_click(e, page),
                    #on_scroll= lambda e: self.handle_scroll_event(e, page),
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
                height= page.height * 0.80,
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
        scroll=ft.ScrollMode.HIDDEN)
        

        return final_table