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

    cell_height = 30
    cell_width = 100

    def highlight_cell(self, cell, page):
        
        if cell not in self.selected_cells:
            cell.border_color = ft.colors.PINK_400
            self.selected_cells.append(cell)
            print(f"Resaltando celda en {cell.row}, {cell.col}")
            page.update()
            


    def unhighlight_cell(self, cell, page):

        if cell in self.selected_cells:
            cell.border_color = ft.colors.GREEN_500
            self.selected_cells.remove(cell)
            print(f"desresaltando celda en {cell.row}, {cell.col}")
            page.update()

    
    def on_keyboard_event(self, e:ft.KeyboardEvent, page):
        # Verificar si hay alguna celda seleccionada
        if not self.selected_cells:
            return
        
        # Utilizar la última celda seleccionada
        current_cell = self.selected_cells[-1]

        current_row = current_cell.row
        current_col = current_cell.col
        
        # Primero, verifica si la tecla es alfanumérica y pone el foco en la celda
        if re.match(r'^[a-zA-Z0-9=+\-*/()!@#$%^&*<>?{}[\]~`|]$', e.key):
            if self.editing_cell != current_cell:
                current_cell.value = ""  # Borra el contenido existente
                self.editing_cell = current_cell  # Actualiza el estado de edición
        
            # Si la tecla es alfanumérica, considera mayúsculas y minúsculas
            if re.match(r'^[a-zA-Z0-9]$', e.key):
                if e.shift:
                    current_cell.value += e.key.upper()
                else:
                    current_cell.value += e.key.lower()
            else:  # Para otros caracteres como '=', '+', '-', etc.
                current_cell.value += e.key
            
            page.update()

        # Manejar el evento de la tecla "Enter"
        if e.key == "Enter":
            if self.editing_cell:  # Verificar si hay una celda en edición
                if self.editing_cell.value.startswith("="):
                    row, col = self.editing_cell.row, self.editing_cell.col
                    evaluate_formula(self.cells, self.editing_cell.value, row, col)  # Evaluar la fórmula
                # Resetear el estado de edición
                self.editing_cell = None  
            page.update()
            return  # Finalizar el manejo del evento aquí, ya que hemos manejado la tecla "Enter"

 
        # Luego, manejar las teclas de flecha
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
        
        
        # Desresaltar la última celda seleccionada
        self.unhighlight_cell(current_cell, page)
        
        # Resaltar la nueva celda seleccionada
        new_selected_cell = self.cells[current_row][current_col]
        self.highlight_cell(new_selected_cell, page)

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

    def on_double_click(self, e: ft.TapEvent):
        print("on double click")
        cell = self.cells[e.control.row][e.control.col]
        cell.focus() #para activar el textfield en escritura    
 

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
       
        print(f"Global X: {e.global_x}, Global Y: {e.global_y}")  # Imprime las coordenadas globales
        print(f"Calculated End Col: {end_col}, Calculated End Row: {end_row}")  # Imprime las columnas y filas calculadas

    def on_pan_end(self, e, page):
        print("Ejecutando on_pan_end")
        self.dragging = False
        self.start_cell = None
        self.end_cell = None  # Limpiar la celda final
        page.update()
    
    def create_table(self, page):

        page.on_keyboard_event = lambda e: self.on_keyboard_event(e, page)

        def on_textfield_change(e):   #se ejecuta cuando se cambia el valor de un textfield
            pass
                #if e.control.value.startswith("="):
                #    row, col = e.control.row, e.control.col
                #    evaluate_formula(self.cells, e.control.value, row, col)  # Llamamos a la función
                #    page.update() 
             
        def on_textfield_focus(e, page):
            self.highlight_cell(e.control, page)

        
        def on_textfield_submit(e):
            # Evaluar la fórmula cuando se presiona Enter
            if e.control.value.startswith("="):
                row, col = e.control.row, e.control.col
                evaluate_formula(self.cells, e.control.value, row, col)
                page.update()


        def on_textfield_blur(e, page):
            self.unhighlight_cell(e.control, page)
            self.editing_cell = None  # Resetear el estado de edición



        textfield_style = {
            'border': ft.InputBorder.OUTLINE,
            'border_color': ft.colors.GREEN_500,
            'hint_text': "",
            'on_change': on_textfield_change,
            'content_padding': 1, 
            'border_width': 0.3,
            'border_radius': 0.2,
            'on_focus': lambda e: on_textfield_focus(e, page),
            'on_blur': on_textfield_blur,
            'text_size': 12,
            'on_submit': on_textfield_submit,

        }       

        

        table_width = self.cell_width * self.COLS + 10  # Añadir un pequeño margen
        table_height = self.cell_height * self.ROWS - 90
        
        #crear filas y columnas para la tabla usando bucles
        table_rows = []
        for r in range(self.ROWS):
            row_cells = []
            for c in range(self.COLS):
                tf = ft.TextField(**textfield_style, height=self.cell_height, width=self.cell_width)  
                tf.row, tf.col = r, c
                self.cells[r][c] = tf

                gd = ft.GestureDetector(
                    mouse_cursor=ft.MouseCursor.MOVE,
                    on_pan_start=lambda e: self.on_pan_start(e, page),
                    on_pan_update=lambda e: self.on_pan_update(e, page),
                    on_pan_end=lambda e: self.on_pan_end(e, page),
                    on_tap=lambda e: self.on_single_click(e, page),
                    on_double_tap=lambda e: self.on_double_click(e)
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
                
            table_rows.append(ft.Row(row_cells, spacing=0))
            

        # Crear una columna con todas las filas para permitir desplazamiento vertical
        table_column = ft.Column(table_rows, spacing=0, scroll=ft.ScrollMode.ALWAYS, height=table_height)

        # Envolver la columna en un contenedor Row para desplazamiento horizontal
        scrollable_row = ft.Row([table_column], spacing=0, scroll=ft.ScrollMode.ALWAYS, width=table_width)

       

        return scrollable_row