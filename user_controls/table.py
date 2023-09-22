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
        
        # Desresaltar la última celda seleccionada
        self.unhighlight_cell(current_cell,page)
        
        # Resaltar la nueva celda seleccionada
        new_selected_cell = self.cells[current_row][current_col]
        self.highlight_cell(new_selected_cell, page)
        new_selected_cell.focus()

        print(self.selected_cells)


    def on_single_click(self, e: ft.TapEvent, page):
        print("On single click")
        cell = self.cells[e.control.row][e.control.col]
        if cell not in self.selected_cells:
            self.highlight_cell(cell, page)
        else:
            self.unhighlight_cell(cell, page)

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
        
    
    def on_pan_update(self, e: ft.DragUpdateEvent, page):
        print("ejecutando on_pan_update")
        if not self.dragging:
            return
        col = int(e.global_x // self.cell_width)
        row = int(e.global_y // self.cell_height)
        if 0 <= row < self.ROWS and 0 <= col < self.COLS:
            cell = self.cells[row][col]
            self.highlight_cell(cell, page)
        

    def on_pan_end(self, e, page):
        print("Ejecutando on_pan_end")
        self.dragging = False
        self.start_cell = None
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