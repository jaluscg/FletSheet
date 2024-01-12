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



 
    def load_excel_data(self, filepath):
        workbook = openpyxl.load_workbook(filepath, data_only=True)
        data = {}
        for sheet in workbook.sheetnames:
            worksheet = workbook[sheet]
            data[sheet] = [[cell.value for cell in row] for row in worksheet.iter_rows()]
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
    

    def highlight_cell(self, cell, page):
        
        if cell not in self.selected_cells:
            cell.border = ft.border.all(0.5, ft.colors.PINK_400)
            self.selected_cells.append(cell)
            print(f"Resaltando celda en {cell.row}, {cell.col}")
            page.update()
            


    def unhighlight_cell(self, cell, page):

        if cell in self.selected_cells:
            cell.border = ft.border.all(0.3, ft.colors.GREEN_500)
            self.selected_cells.remove(cell)
            print(f"desresaltando celda en {cell.row}, {cell.col}")
            page.update()


            

    def on_keyboard_event(self, e:ft.KeyboardEvent, page):

        def almacenar_datoescrito(current_row, current_col, current_cell, previous_value):
            adjusted_row = current_row + self.visible_start_row 
            adjusted_col = current_col + self.visible_start_col 

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

        if e.ctrl == True:
            #print("se oprimió ctrl")
            if e.key.lower() == "c":
                start_row, start_col = self.selected_cells[0].row, self.selected_cells[0].col
                end_row, end_col = self.selected_cells[-1].row, self.selected_cells[-1].col
                self.clipboard = []
                clipboard_str = ""  # Una cadena para almacenar el contenido en formato de texto plano
                for row in range(start_row, end_row+1):
                    row_values = []
                    row_str_values = []  # Almacena los valores de la fila como cadenas
                    for col in range(start_col, end_col+1):
                        value = self.cells[row][col].content.value
                        row_values.append(value)
                        row_str_values.append(str(value))
                    self.clipboard.append(row_values)
                    clipboard_str += "\t".join(row_str_values) + "\n"  # Separar las celdas con tabuladores y las filas con saltos de línea

                # Actualizar el portapapeles del sistema
                page.set_clipboard(clipboard_str)

                print(f"Contenido copiado: {self.clipboard}")

            elif e.key.lower() == "v":
                clipboard_content = page.get_clipboard()  # Obtener el contenido del portapapeles
                if clipboard_content:
                    # Dividir el contenido en filas y celdas
                    rows = clipboard_content.split("\n")
                    matrix = [row.split("\t") for row in rows]

                    # Pegar este contenido en tu programa
                    if self.selected_cells:  # Verificar que hay una celda seleccionada donde pegar
                        start_row, start_col = self.selected_cells[-1].row, self.selected_cells[-1].col
                        for i, row_values in enumerate(matrix):
                            for j, value in enumerate(row_values):
                                row = start_row + i
                                col = start_col + j
                                if 0 <= row < self.ROWS and 0 <= col < self.COLS:
                                    current_cell = self.cells[row][col]
                                    previous_value = current_cell.content.value
                                    current_cell.content.value = value
                                    almacenar_datoescrito(row, col, current_cell, previous_value)  # Actualizar self.edited_cells
                                    if value.startswith("="):  # Si es una fórmula
                                        evaluate_formula(self.cells, value, row, col)  # Evaluar fórmulas         

                    page.update()

            elif e.key.lower() == "x":
                if self.selected_cells:
                    start_row, start_col = self.selected_cells[0].row, self.selected_cells[0].col
                    end_row, end_col = self.selected_cells[-1].row, self.selected_cells[-1].col
                    self.clipboard = []
                    clipboard_str = ""  # Una cadena para almacenar el contenido en formato de texto plano
                    for row in range(start_row, end_row + 1):
                        for col in range(start_col, end_col + 1):
                            current_cell = self.cells[row][col]
                            previous_value = current_cell.content.value  # Capturar el valor anterior
                            current_cell.content.value = ""
                            almacenar_datoescrito(row, col, current_cell, previous_value)
                        self.clipboard.append(row_values)
                        clipboard_str += "\t".join(row_str_values) + "\n"  # Separar las celdas con tabuladores y las filas con saltos de línea

                    # Actualizar el portapapeles del sistema
                    page.set_clipboard(clipboard_str)
                    #print(f"Contenido cortado: {self.clipboard}")
                    page.update()
                
            elif e.key.lower() == "z":
                 if self.undo_stack:
                    change_type, sheet_name, row, col, old_value, new_value = self.undo_stack.pop()
                    print(f"stack.pop: {self.undo_stack.pop()} ")
                    print(f"Deshaciendo: {change_type}, fila: {row}, columna: {col}, valor anterior: {old_value}, valor nuevo: {new_value}")
                    
                    # Actualizar la celda específica con el valor antiguo
                    self.cells[row][col].content.value = old_value

                    # Actualizar el diccionario de celdas editadas
                    sheet_name = self.current_sheet
                    if sheet_name not in self.edited_cells:
                        self.edited_cells[sheet_name] = {}
                    self.edited_cells[sheet_name][(row + 1, col + 1)] = old_value  # Asegurarse de que las coordenadas se ajusten a la estructura de edited_cells

                    page.update()


        # Luego, manejar las teclas de flecha
    
    
        scroll_needed = False
        mirar_scroll_needed = self.selected_cells[0]

        row_scroll_needed = mirar_scroll_needed.row
        col_scroll_needed = mirar_scroll_needed.col
       

        if not self.double_clicked:

            if e.shift and self.start_cell is None:
                # Si 'Shift' está presionado y no hay una celda de inicio establecida,
                # se establece la celda actual como la celda de inicio antes de moverse.
                self.start_cell = self.cells[current_row][current_col]
                print(f"Estableciendo start_cell a ({self.start_cell.row}, {self.start_cell.col}) al inicio de la selección")

            self.end_cell = self.cells[current_row][current_col]

              # La lógica para moverse entre las celdas se mantiene igual
            if e.key == "Arrow Up" and row_scroll_needed == self.visible_start_row:
                scroll_needed = True
                print("scroll arriba")
                print(f"acual row scorll needed: {row_scroll_needed} y actual col needed {col_scroll_needed} ")
                print( f"limite row {self.visible_start_row} limite col {self.visible_start_col}")

                current_row -= 1

            elif e.key == "Arrow Down" and row_scroll_needed == self.visible_end_row -1:
                scroll_needed = True
                print("Scroll Abajo")
                print(f"acual row scorll needed: {row_scroll_needed} y actual col needed {col_scroll_needed} ")
                print( f"limite row {self.visible_end_row} limite col {self.visible_end_col}")
                
                current_row += 1

            elif e.key == "Arrow Left" and col_scroll_needed == self.visible_start_col:
                scroll_needed = True
                print("scroll izquierda")
                print(f"acual row scorll needed: {row_scroll_needed} y actual col needed {col_scroll_needed} ")
                print( f"limite row {self.visible_start_row} limite col {self.visible_start_col}")
                current_col -= 1

            elif e.key == "Arrow Right" and col_scroll_needed == self.visible_end_col-1:
                scroll_needed = True
                print("scroll derecha")
                print(f"acual row scorll needed: {row_scroll_needed} y actual col needed {col_scroll_needed} ")
                print( f"limite row {self.visible_end_row} limite col {self.visible_end_col}")
                current_col += 1


            elif e.key == "Arrow Up" and current_row > 0:
                current_row -= 1
                

            elif e.key == "Arrow Down" and current_row < self.ROWS - 1:
                current_row += 1
                print(f"acual row scorll needed: {row_scroll_needed} y actual col needed {col_scroll_needed} ")
                print( f"limite row {self.visible_end_row} limite col {self.visible_end_col}")
                

            elif e.key == "Arrow Left" and current_col > 0:
                current_col -= 1
                

            elif e.key == "Arrow Right" and current_col < self.COLS - 1:
                current_col += 1
                
                   
            else:
                return
            
            if scroll_needed:

                cell = self.cells[row_scroll_needed][col_scroll_needed]
                self.end_cell = cell
                # Si se necesita desplazamiento, actualiza los índices de las filas/columnas visibles
                if e.key == "Arrow Up":
                    
                    
                    self.visible_end_row = max(self.visible_end_row - 1, self.ROWS)
                    self.visible_start_row =  max(self.visible_start_row -1, 0)

                


                elif e.key == "Arrow Down":

                    self.visible_end_row = self.ROWS
                    self.visible_start_row = self.visible_start_row +1



                elif e.key == "Arrow Left":
                

                    self.visible_start_col = max(self.visible_start_col - 1, 0)
                    self.visible_end_col = max(self.visible_end_col -1, self.COLS)

                    


                elif e.key == "Arrow Right":
                

                    self.visible_start_col = self.visible_start_col +1
                    self.visible_end_col = self.COLS


                # Actualiza las celdas visibles y la interfaz de usuario
                self.update_visible_cells()
                self.update_indices()
                page.update()


            # Si 'Shift' está presionado, resaltar la nueva celda
            if not scroll_needed:
                cell = self.cells[current_row][current_col]
                self.end_cell = cell
            
            

            if e.shift:
                
                if self.start_cell is None :
                    # Actualizar la celda inicial para la nueva selección
                    self.start_cell = cell
                    print(f"Estableciendo start_cell a ({self.start_cell.row}, {self.start_cell.col}) porque se presionó shift")
        
                start_row, start_col = self.start_cell.row , self.start_cell.col 
                end_row, end_col = self.end_cell.row, self.end_cell.col

                new_selected_cells = []
                for row in range(min(start_row, end_row), max(start_row, end_row) + 1):
                    for col in range(min(start_col, end_col), max(start_col, end_col) + 1):
                        new_selected_cells.append(self.cells[row][col])

                for cell in self.selected_cells:
                    if cell not in new_selected_cells:
                        self.unhighlight_cell(cell, page)

                for cell in new_selected_cells:
                    if cell not in self.selected_cells:
                        self.highlight_cell(cell, page)

                self.selected_cells = new_selected_cells

                print(f"Current row: {current_row}, Current col: {current_col}")
                print(f"Start row: {start_row}, Start col: {start_col}")
                print(f"End row: {end_row}, End col: {end_col}")

                if not e.shift:
                    self.clear_all_highlights(page)
                    self.highlight_cell(cell, page)
                    start_row = None
                    start_col = None
                    #print(f"la start cell es: {self.start_cell} ")
            else:
                self.clear_all_highlights(page)
                self.highlight_cell(cell, page)
                self.start_cell = None  # Reset the start cell
                #print(f"la start cell está en: {self.start_cell} ")

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
        self.double_clicked = False
        

    def on_double_click(self, e: ft.TapEvent, page):
        self.double_clicked = True
        cell = self.cells[e.control.row][e.control.col]
        cell.original_value = cell.content.value  # Guarda el valor original
        self.editing_cell = cell  # Establece que esta celda está siendo editada

         # Crear un TextField con el mismo tamaño, contenido que la celda y autofocus activado
        text_field = ft.TextField(value=cell.content.value, width=self.cell_width, height=self.cell_height, autofocus=True)
        text_field.on_submit = lambda e: self.on_textfield_submit(e, page, cell)
        cell.content = text_field  # Reemplaza el contenido de la celda con el TextField
        page.update()
    
    def on_textfield_submit(self, e, page, cell):
        # Guardar el valor del TextField en la celda
        new_value = e.control.value
        if new_value.startswith("="):
            # Tratar como fórmula
            cell.formula = new_value
            evaluated_value = evaluate_formula(new_value)  # Implementar esta función según sea necesario
            cell.content = ft.Text(evaluated_value)
        else:
            # Tratar como texto normal
            cell.content = ft.Text(new_value)

        # Actualizar la celda y quitar el modo de edición
        self.double_clicked = False
        page.update()


    def on_pan_start(self, e: ft.DragStartEvent, page):
        print("ejecutando on_pan_start")
        for cell in self.selected_cells:
            self.unhighlight_cell(cell, page)
        self.selected_cells.clear()
        self.dragging = True
        cell = self.cells[e.control.row][e.control.col]
        self.highlight_cell(cell, page)
        self.start_cell = cell
        self.end_cell = None  # Nueva variable para almacenar la celda final


    def on_pan_update(self, e: ft.DragUpdateEvent, page):
        if not self.dragging or self.start_cell is None:
            return

        end_col = int((e.global_x) // self.cell_width) - 1
        end_row = int((e.global_y) // self.cell_height) - 3

   
        # Actualizar solo si la celda final ha cambiado
        if self.end_cell is None or end_row != self.end_cell.row or end_col != self.end_cell.col:
            self.end_cell = self.cells[end_row][end_col]

            # Identificar las nuevas celdas que deberían estar seleccionadas
            start_row, start_col = self.start_cell.row, self.start_cell.col
            end_row, end_col = self.end_cell.row, self.end_cell.col

            new_selected_cells = []

            for row in range(min(start_row, end_row), max(start_row, end_row) + 1):
                for col in range(min(start_col, end_col), max(start_col, end_col) + 1):
                    if 0 <= row < self.ROWS and 0 <= col < self.COLS:
                        new_selected_cells.append(self.cells[row][col])

            # Desresaltar las celdas que ya no están en el rango seleccionado
            for cell in self.selected_cells:
                if cell not in new_selected_cells:
                    self.unhighlight_cell(cell, page)

            # Resaltar las nuevas celdas seleccionadas
            for cell in new_selected_cells:
                if cell not in self.selected_cells:
                    self.highlight_cell(cell, page)

            self.selected_cells = new_selected_cells  # Actualizar la lista de celdas seleccionadas
       
        #print(f"Global X: {e.global_x}, Global Y: {e.global_y}")  # Imprime las coordenadas globales
        #print(f"Calculated End Col: {end_col}, Calculated End Row: {end_row}")  # Imprime las columnas y filas calculadas

    def on_pan_end(self, e, page):
        print("Ejecutando on_pan_end")
        self.dragging = False
        self.start_cell = None
        self.end_cell = None  # Limpiar la celda final
        page.update()
    
    def add_row(self, e, page):
        container_style = {
            'border': ft.border.all(0.3, ft.colors.GREEN_500),
            'border_radius': 0.2,
            'height': self.cell_height,
            'width': self.cell_width,
        }

        new_row_index = self.ROWS
        self.ROWS += 1
        new_row = []

        # Añadir una nueva fila vacía a la matriz de celdas.
        self.cells.append([None] * self.COLS)

        for c in range(self.COLS):
            tf = ft.Container(**container_style, content=Text(""))
            tf.row, tf.col = new_row_index, c
            tf.formula = None
            self.cells[new_row_index][c] = tf

            gd = ft.GestureDetector(
                mouse_cursor=ft.MouseCursor.MOVE,
                on_pan_start=lambda e: None if self.is_mobile_device(page) or self.is_packege_device(page) else self.on_pan_start(e, page),
                on_pan_update=lambda e: None if self.is_mobile_device(page) or self.is_packege_device(page) else self.on_pan_update(e, page),
                on_pan_end=lambda e: None if self.is_mobile_device(page) or self.is_packege_device(page) else self.on_pan_end(e, page),
                on_tap=lambda e: self.on_single_click(e, page),
                on_double_tap=lambda e: self.on_double_click(e, page),
            )

            gd.row, gd.col = new_row_index, c

            stacked_cell = ft.Stack(
                [
                    tf,
                    gd
                ],
                width=self.cell_width,
                height=self.cell_height
            )

            new_row.append(stacked_cell)

        # Añadir la nueva fila a las filas de la tabla
        self.table_rows.append(ft.Row(new_row, spacing=0))

        

        Row_button_style = {
            'border': ft.border.all(0.3, ft.colors.GREY),
            'border_radius': 0.2,
            'height': self.cell_height,
            'width': self.cell_height,
            'bgcolor': ft.colors.BLUE_GREY_50,
        }

        row_index_control = ft.Container(
            **Row_button_style,
            content=ft.Text(str(new_row_index + 1)),  # +1 para el índice basado en 1
            on_click= lambda e, row=new_row_index: self.on_row_index_clicked(e, page, row),
        )

        # Añadir el nuevo control de índice al final de `self.row_indices_controls`
        self.row_indices_controls.append(row_index_control)
        
        # Actualizar el control de índices de columna en la interfaz de usuario si existe
        if hasattr(self, 'row_indices'):
            self.row_indices.controls.append(row_index_control)
            self.row_indices.update()


        if self.table_initialized:  # Comprobar si la tabla se ha inicializado
            page.update()


    def add_col(self, e, page):
        container_style = {
            'border': ft.border.all(0.3, ft.colors.GREEN_500),
            'border_radius': 0.2,
            'height': self.cell_height,
            'width': self.cell_width,
        }

        new_col_index = self.COLS
        self.COLS += 1

        # Añadir una nueva columna a cada fila en la matriz de celdas
        for r in range(self.ROWS):
            tf = ft.Container(**container_style, content=ft.Text(""))
            tf.row, tf.col = r, new_col_index
            tf.formula = None
            self.cells[r].append(tf)

            gd = ft.GestureDetector(
                mouse_cursor=ft.MouseCursor.MOVE,
                on_pan_start=lambda e: None if self.is_mobile_device(page) or self.is_packege_device(page) else self.on_pan_start(e, page),
                on_pan_update=lambda e: None if self.is_mobile_device(page) or self.is_packege_device() else self.on_pan_update(e, page),
                on_pan_end=lambda e: None if self.is_mobile_device(page) or self.is_packege_device() else self.on_pan_end(e, page),    
                on_tap=lambda e: self.on_single_click(e, page),
                on_double_tap=lambda e: self.on_double_click(e, page),

            )

            gd.row, gd.col = r, new_col_index

            stacked_cell = ft.Stack(
                [
                    tf,
                    gd
                ],
                width=self.cell_width,
                height=self.cell_height
            )

            # Añadir la nueva celda al final de la fila correspondiente
            self.table_rows[r].controls.append(stacked_cell)

        # Crear el control para el índice de la nueva columna fuera del bucle for
        column_button_style = {
            'height': self.cell_height,
            'width': self.cell_width,
            'bgcolor': ft.colors.BLUE_GREY_50,
            'border': ft.border.all(0.3, ft.colors.GREY),
            'border_radius': 0.2,
        }

        new_index_label = self.num_to_excel_col(new_col_index)
        new_index_control = ft.Container(
            **column_button_style,
            content=ft.Text(new_index_label),
            on_click=lambda e, col=new_col_index: self.on_column_index_clicked(e, page, col),
        )

        # Añadir el nuevo control de índice al final de `self.column_indices_controls`
        self.column_indices_controls.append(new_index_control)

        # Actualizar el control de índices de columna en la interfaz de usuario si existe
        if hasattr(self, 'column_indices'):
            self.column_indices.controls.append(new_index_control)
            self.column_indices.update()

        if self.table_initialized:  # Comprobar si la tabla se ha inicializado
            page.update()


    
    def on_column_index_clicked(self, e, page, col_index):
        for r in range(self.ROWS):
            self.cells[r][col_index].border = ft.colors.BLUE_100
        page.update()

    def on_row_index_clicked(self, e, page, row_index):
        for c in range(self.COLS):
            self.cells[row_index][c].border = ft.colors.BLUE_100
        page.update()

    
    @staticmethod
    def num_to_excel_col(num):
        """
        Convert a zero-indexed number to a string representing its Excel column name.
        For example, 0 -> 'A', 1 -> 'B', ..., 26 -> 'AA', etc.
        """
        excel_col = ''
        while num >= 0:
            num, remainder = divmod(num, 26)
            excel_col = chr(65 + remainder) + excel_col
            num -= 1
        return excel_col
    

    def create_indices(self, page):
        # Establecemos estilos para los contenedores de índices
        special_column_button_style = {
            'height': self.cell_height,
            'width': self.cell_height,
            'bgcolor': ft.colors.BLUE_GREY_50,
            'border': ft.border.all(0.3, ft.colors.GREY),
            'border_radius': 0.2,
        }
        
        column_button_style = {
            'height': self.cell_height,
            'width': self.cell_width,
            'bgcolor': ft.colors.BLUE_GREY_50,
            'border': ft.border.all(0.3, ft.colors.GREY),
            'border_radius': 0.2,
        }
        
        row_button_style = {
            'height': self.cell_height,
            'width': 30,  # Ancho fijo para los índices de fila
            'bgcolor': ft.colors.BLUE_GREY_50,
            'border': ft.border.all(0.3, ft.colors.GREY),
            'border_radius': 0.2,
        }

        # Creamos el contenedor especial para el índice de columna separado
        special_column_container = ft.Container(
            **special_column_button_style,
            content=ft.Icon(name=ft.icons.BEACH_ACCESS, color=ft.colors.PINK),
            on_click=lambda e: self.on_special_column_clicked(e, page),
        )
        
        # Creamos los índices de columnas regulares
        column_indices_controls = [special_column_container]  # Iniciamos con el contenedor especial
        for c in range(self.COLS):
            column_label = self.num_to_excel_col(c)
            btn = ft.Container(
                **column_button_style,
                content=Text(column_label),
                on_click=lambda e, col=c: self.on_column_index_clicked(e, page, col),
            )
            column_indices_controls.append(btn)
        column_indices = ft.Row(column_indices_controls, spacing=0)

        # Creamos los índices de filas
        row_indices_controls = []
        for r in range(self.ROWS):
            btn = ft.Container(
                **row_button_style,
                content=Text(str(r + 1)),
                on_click=lambda e, row=r: self.on_row_index_clicked(e, page, row),
            )
            row_indices_controls.append(btn)
        row_indices = ft.Column(row_indices_controls, spacing=0)

        self.column_indices_controls = column_indices_controls
        self.row_indices_controls = row_indices_controls

        return column_indices, row_indices


    def update_indices(self):
        # Actualizar índices de columnas
        for c in range(self.COLS):
            column_label = self.num_to_excel_col(c + self.visible_start_col)
            self.column_indices_controls[c + 1].content = Text(column_label)  # +1 porque el primer control es especial

        # Actualizar índices de filas
        for r in range(self.ROWS):
            row_label = str(r + self.visible_start_row + 1)
            self.row_indices_controls[r].content = Text(row_label)


    def handle_vertical_scroll_event(self, e):
        # Asegúrate de que el evento es de tipo 'update'
        if e.event_type == "update":
            # Calcular los índices de fila y columna basándose en el desplazamiento del scroll
            self.dragging = False

            # Suponiendo que scroll_delta representa el desplazamiento en Y (vertical)
            delta_rows = int(e.scroll_delta / self.cell_height)

            # Ajusta tus índices de fila de acuerdo al desplazamiento
            self.visible_start_row = max(0, self.visible_start_row + delta_rows)
            self.visible_end_row = min(self.ROWS, self.visible_start_row + 12)

            # Para desplazamiento horizontal, necesitarás una lógica similar
            # pero dependiendo de cómo captures el desplazamiento horizontal
            # delta_cols = ...
            # self.visible_start_col = max(0, self.visible_start_col + delta_cols)
            # self.visible_end_col = min(self.COLS, self.visible_start_col + 10)

            # Actualizar celdas visibles
            self.update_visible_cells()
            self.update_indices()
            e.page.update()
    
    def handle_horizontal_scroll_event(self, e):
        # Asegúrate de que el evento es de tipo 'update'
        if e.event_type == "update":
            # Calcular el cambio en las columnas basándose en el desplazamiento del scroll
            self.dragging = False

            # Suponiendo que scroll_delta representa el desplazamiento en X (horizontal)
            delta_cols = int(e.scroll_delta / self.cell_width)

            # Ajusta tus índices de columna de acuerdo al desplazamiento
            self.visible_start_col = max(0, self.visible_start_col + delta_cols)
            self.visible_end_col = min(self.COLS, self.visible_start_col + 10)

            # Actualizar celdas visibles
            self.update_visible_cells()
            self.update_indices()
            e.page.update()



    def load_excel_data(self, filepath):
        print("se está cargando data excel")
        workbook = openpyxl.load_workbook(filepath, data_only=True)
        data = {}

        # Iterar sobre todas las hojas en el libro de trabajo
        for sheet_name in workbook.sheetnames:
            worksheet = workbook[sheet_name]
            sheet_data = []
            for row in worksheet.iter_rows():
                row_data = []
                for cell in row:
                    # Aquí puedes acceder a los estilos de la celda si es necesario
                    # Por ejemplo: cell.font, cell.border, cell.fill, etc.
                    cell_value = cell.value
                    row_data.append(cell_value)
                sheet_data.append(row_data)
            data[sheet_name] = sheet_data

        return data

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
                

    def on_horizontal_slider_change(self, e, page):
        # Calcula el desplazamiento en las columnas basado en el valor del slider
        self.visible_start_col = int(e.control.value)
        self.visible_end_col = self.visible_end_col
        e.max_scroll_extent = 1000
        self.update_visible_cells()
        self.update_indices()
        page.update()


    def on_vertical_slider_change(self, e, page):
        # Calcula el desplazamiento en las filas basado en el valor del slider
        self.visible_start_row = int(e.control.value)
        self.visible_end_row = self.visible_end_row
        print(f"e.max_scroll_extent: {e.max_scroll_extent}")
        self.update_visible_cells()
        self.update_indices()
        page.update()

    
    def create_sheets_section(self, page):
        """
        Crea una sección con botones para cada hoja de Excel.
        """
        buttons = []
        for sheet_name in self.excel_data.keys():
            btn = ft.TextButton(
                text=sheet_name,
                on_click=lambda e, name=sheet_name: self.on_sheet_selected(e, page, name)
            )
            buttons.append(btn)
        return ft.Row(buttons)

    def on_sheet_selected(self, e, page, sheet_name):
        """
        Maneja la selección de una hoja de Excel.
        """
        self.current_sheet = sheet_name
        self.btn_hoja = True
        self.update_visible_cells()  # Asegúrate de que esta función use self.current_sheet
        page.update()
        self.btn_hoja = False

    def is_mobile_device(self, page):
        pass

    def is_packege_device(self, page):
        # verificar si es un dispositivo empaquetado
        if getattr(sys, 'frozen', False):
            # En un entorno empaquetado
            return True
        else:
            # En un entorno de desarrollo
            return False
    
    
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