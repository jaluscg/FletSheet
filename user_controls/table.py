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

    cell_height = 30
    cell_width = 100

    def highlight_cell(self, cell):
        if cell not in self.selected_cells:
            cell.border_color = ft.colors.BLUE_100
            self.selected_cells.append(cell)

    def unhighlight_cell(self, cell):
        if cell in self.selected_cells:
            cell.border_color = ft.colors.GREEN_500
            self.selected_cells.remove(cell)
    
    def on_keyboard_event(self, e:ft.KeyboardEvent):
        #mirar si hay alguna celda seleccionada
        if not self.selected_cells:
            return
        
        #Usar última celda seleccionada
        current_cell = self.selected_cells[-1]

        current_row = current_cell.row
        current_col = current_cell.col

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
        
        self.unhighlight_cell(self.selected_cells)
        new_selected_cell = self.cells[current_row][current_col]
        self.highlight_cell(new_selected_cell)
        new_selected_cell.focus()


    def on_click(self, e: ft.TapEvent):
        print("On cick")
        cell = self.cells[e.control.row][e.control.col]
        self.dragging = False #Asegurarse de que no estemos arrastrando
        self.cell.highlight_cell(cell)

        
    def on_pan_start(self, e: ft.DragStartEvent):
        ("ejecutando on_pan_start")
        for cell in self.selected_cells:
            self.unhighlight_cell(cell)
        self.selected_cells.clear()
        self.dragging = True
        cell = self.cells[e.control.row][e.control.col]
        self.highlight_cell(cell)
        self.start_cell = cell
        

    def on_pan_update(self, e: ft.DragUpdateEvent):
        print("ejecutando on_pan_update")
        if not self.dragging:
            return
        col = int(e.global_x // self.cell_width)
        row = int(e.global_y // self.cell_height)
        if 0 <= row < self.ROWS and 0 <= col < self.COLS:
            cell = self.cells[row][col]
            self.highlight_cell(cell)

    def on_pan_end(self, e):
        print("Ejecutando on_pan_end")
        self.dragging = False
        self.start_cell = None


    def create_table(self, page):

        page.on_keyboard_event = self.on_keyboard_event

        def on_textfield_change(e):   #se ejecuta cuando se cambia el valor de un textfield
            pass
                #if e.control.value.startswith("="):
                #    row, col = e.control.row, e.control.col
                #    evaluate_formula(self.cells, e.control.value, row, col)  # Llamamos a la función
                #    page.update() 
             
        def on_textfield_focus(e):
            self.highlight_cell(e.control)

        
        def on_textfield_submit(e):
            # Evaluar la fórmula cuando se presiona Enter
            if e.control.value.startswith("="):
                row, col = e.control.row, e.control.col
                evaluate_formula(self.cells, e.control.value, row, col)
                page.update()


        def on_textfield_blur(e):
            self.unhighlight_cell(e.control)
            # Evaluar la fórmula cuando la celda pierde el foco
            if e.control.value.startswith("="):
                row, col = e.control.row, e.control.col
                evaluate_formula(self.cells, e.control.value, row, col)
                page.update()



        textfield_style = {
            'border': ft.InputBorder.OUTLINE,
            'border_color': ft.colors.GREEN_500,
            'hint_text': "",
            'on_change': on_textfield_change,
            'content_padding': 1, 
            'border_width': 0.3,
            'border_radius': 0.2,
            'on_focus': on_textfield_focus,
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
                    on_pan_start=self.on_pan_start,
                    on_pan_update=self.on_pan_update,
                    on_pan_end=self.on_pan_end,
                    on_tap=self.on_click,
                    content=tf  # Coloca el TextField dentro del GestureDetector
                )
                
                row_cells.append(gd)
                
            # No necesitas envolver la fila en otro contenedor Row
            table_rows.append(ft.Row(row_cells, spacing=0))


        # Crear una columna con todas las filas para permitir desplazamiento vertical
        table_column = ft.Column(table_rows, spacing=0, scroll=ft.ScrollMode.ALWAYS, height=table_height)

        # Envolver la columna en un contenedor Row para desplazamiento horizontal
        scrollable_row = ft.Row([table_column], spacing=0, scroll=ft.ScrollMode.ALWAYS, width=table_width)

        return scrollable_row
      
        
      
       

