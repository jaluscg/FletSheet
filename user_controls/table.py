import flet as ft
from flet import *
import re
from .funciones import evaluate_formula

class TextFieldTable:
    def __init__(self, rows, cols):
        self.ROWS = rows
        self.COLS = cols
        self.selected_cells = [] #inicializar como lista vacía
        self.cells =  [[None for _ in range(self.COLS)] for _ in range(self.ROWS)]  # Matriz de celdas
        self.dragging = False
        self.double_clicked = False
        self.current_selected_cell = None
        self.explicitly_selected_cells = []
        self.editing_cell = None
        self.clipboard = [] #contenido copiado o cortado puede ser una lista
        self.double_clicked = False
        self.visible_start_row = 0
        self.visible_end_row = 20  # Ajustar según el tamaño de la ventana de visualización
        self.visible_start_col = 0
        self.visible_end_col = 10  # Ajustar según el tamaño de la ventana de visualización
        self.start_cell = None 
        self.table_rows = []
        self.table_initialized = False  # Inicializa el estado de la tabla


    cell_height = 30
    cell_width = 100

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
        #print(f"Evento de teclado completo: {e}")
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
                                    self.cells[row][col].content.value = value
                                    if value.startswith("="):  # Si es una fórmula
                                        evaluate_formula(self.cells, value, row, col)  # Asume que tienes una función para evaluar fórmulas
    
                    page.update()

            elif e.key.lower() == "x":
                if self.selected_cells:
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
                            self.cells[row][col].content.value = ""  # Borra el contenido de la celda
                        self.clipboard.append(row_values)
                        clipboard_str += "\t".join(row_str_values) + "\n"  # Separar las celdas con tabuladores y las filas con saltos de línea

                    # Actualizar el portapapeles del sistema
                    page.set_clipboard(clipboard_str)
                    print(f"Contenido cortado: {self.clipboard}")
                    page.update()

        # Luego, manejar las teclas de flecha

            
        
        if not self.double_clicked:
            if e.shift and self.start_cell is None:
                # Si 'Shift' está presionado y no hay una celda de inicio establecida,
                # se establece la celda actual como la celda de inicio antes de moverse.
                self.start_cell = self.cells[current_row][current_col]
                print(f"Estableciendo start_cell a ({self.start_cell.row}, {self.start_cell.col}) al inicio de la selección")

            self.end_cell = self.cells[current_row][current_col]

            # La lógica para moverse entre las celdas se mantiene igual
            if e.key == "Arrow Up" and current_row > 0:
                current_row -= 1
            elif e.key == "Arrow Down" and current_row < self.ROWS - 1:
                current_row += 1
            elif e.key == "Arrow Left" and current_col > 0:
                current_col -= 1
            elif e.key == "Arrow Right" and current_col < self.COLS - 1:
                current_col += 1
            else:
                return

            # Si 'Shift' está presionado, resaltar la nueva celda
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
                    print(f"la start cell es: {self.start_cell} ")
            else:
                self.clear_all_highlights(page)
                self.highlight_cell(cell, page)
                self.start_cell = None  # Reset the start cell
                print(f"la start cell está en: {self.start_cell} ")

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
        cell.original_value = cell.content.value  # Guarda el valor original
        self.editing_cell = cell  # Establece que esta celda está siendo editada
  
 

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

        end_col = int((e.global_x) // self.cell_width) - 2
        end_row = int((e.global_y) // self.cell_height) - 1


   
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
        if not self.table_initialized:  # Comprueba si la tabla se ha inicializado
            return  # Salir de la función si la tabla no se ha inicializado

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
                on_pan_start=lambda e: self.on_pan_start(e, page),
                on_pan_update=lambda e: self.on_pan_update(e, page),
                on_pan_end=lambda e: self.on_pan_end(e, page),
                on_tap=lambda e: self.on_single_click(e, page),
                on_double_tap=lambda e: self.on_double_click(e, page)
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

        #page.update()


    def add_col(self, e, page):

        if not self.table_initialized:  # Comprueba si la tabla se ha inicializado
            return  # Salir de la función si la tabla no se ha inicializado

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
            tf = ft.Container(**container_style, content=Text(""))
            tf.row, tf.col = r, new_col_index
            tf.formula = None
            self.cells[r].append(tf)

            gd = ft.GestureDetector(
                mouse_cursor=ft.MouseCursor.MOVE,
                on_pan_start=lambda e: self.on_pan_start(e, page),
                on_pan_update=lambda e: self.on_pan_update(e, page),
                on_pan_end=lambda e: self.on_pan_end(e, page),
                on_tap=lambda e: self.on_single_click(e, page),
                on_double_tap=lambda e: self.on_double_click(e, page)
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

        #page.update()

    

    def create_table(self, page):




        page.on_keyboard_event = lambda e: self.on_keyboard_event(e, page)


        container_style = {
            'border': ft.border.all(0.3, ft.colors.GREEN_500),
            'border_radius': 0.2,
            'height': self.cell_height,
            'width': self.cell_width,
        }

        
        table_width = self.cell_width * self.COLS + 10  # Añadir un pequeño margen
        table_height = self.cell_height * self.ROWS - 90



        
        #crear filas y columnas para la tabla usando bucles
       
        for r in range(self.ROWS):
            row_cells = []
            for c in range(self.COLS):
                tf = ft.Container(**container_style, content= Text(""))  
                tf.row, tf.col = r, c
                tf.formula = None #Añadirle atributo a la formula
                self.cells[r][c] = tf

                gd = ft.GestureDetector(
                    mouse_cursor=ft.MouseCursor.MOVE,
                    on_pan_start=lambda e: self.on_pan_start(e, page),
                    on_pan_update=lambda e: self.on_pan_update(e, page),
                    on_pan_end=lambda e: self.on_pan_end(e, page),
                    on_tap=lambda e: self.on_single_click(e, page),
                    on_double_tap=lambda e: self.on_double_click(e, page),
                    #on_scroll= lambda e: on_scroll_event(e, page)
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
                
            self.table_rows.append(ft.Row(row_cells, spacing=0))
            

        # Crear una columna con todas las filas para permitir desplazamiento vertical
        table_column = ft.Column(self.table_rows, spacing=0, scroll=ft.ScrollMode.ALWAYS, height=table_height)

        # Envolver la columna en un contenedor Row para desplazamiento horizontal
        scrollable_row = ft.Row([table_column], spacing=0, scroll=ft.ScrollMode.ALWAYS, width=table_width)

        

        return scrollable_row