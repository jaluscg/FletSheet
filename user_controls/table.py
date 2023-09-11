import flet as ft
from flet import *
import re
from .funciones import Funciones

class TextFieldTable:
    def __init__(self, rows, cols):
        self.ROWS = rows
        self.COLS = cols
        self.selected_cell = None
        self.cells =  [[None for _ in range(self.COLS)] for _ in range(self.ROWS)]  # Matriz de celdas

    def highlight_cell(self, cell):
        print("Highlighting cell:", cell)
        cell.border_color = ft.colors.BLUE_100
        self.selected_cell = cell

    def unhiglight_cell(self, cell):
        print("Unhighlighting cell:", cell) 
        cell.border_color = ft.colors.GREEN_500


    def on_keyboard_event(self, e:ft.KeyboardEvent):
        if not self.selected_cell:
            return
        
        current_row = self.selected_cell.row
        current_col = self.selected_cell.col

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
        
        self.unhiglight_cell(self.selected_cell)
        new_selected_cell = self.cells[current_row][current_col]
        self.highlight_cell(new_selected_cell)
        new_selected_cell.focus()

    
    def create_table(self, page):

        page.on_keyboard_event = self.on_keyboard_event

            
        def evaluate_formula(self, formula, row, col):
    
            # Fórmula =SUM(A1, A2, ...)
            match_sum = re.match(r"=SUM\((?P<args>[A-Z]\d(?:,[A-Z]\d)*)\)", formula)
            if match_sum:
                args = match_sum.group('args').split(',')
                result = Funciones.SUM(self.cells, *args)  # Aquí ya no pasamos 'self'
                self.cells[row][col].value = str(result)
                return

            # Fórmula =ADD(A1,5,A2,...)
            match_add = re.match(r"=ADD\((?P<args>[A-Z]\d|[\d.]+(?:,[A-Z]\d|[\d.]+)*)\)", formula)
            if match_add:
                args = match_add.group('args').split(',')
                result = Funciones.ADD(self.cells, *args)  # Aquí ya no pasamos 'self'
                self.cells[row][col].value = str(result)
                return

            # Fórmula general que puede contener operaciones y referencias a celdas
            def replace_cell_reference(match):
                r = int(match.group(2)) - 1
                c = ord(match.group(1)) - 65
                return str(self.cells[r][c].value)
            
            formula_eval = re.sub(r'([A-Z])(\d+)', replace_cell_reference, formula[1:])  # Usamos [1:] para omitir el signo "=" al principio

            try:
                result = eval(formula_eval)
                self.cells[row][col].value = str(result)
            except Exception as e:
                self.cells[row][col].value = "Error"


                    



        def on_textfield_change(e):   #se ejecuta cuando se cambia el valor de un textfield
             if e.control.value.startswith("="):
                  row, col = e.control.row, e.control.col
                  evaluate_formula(e.control.value, row, col)
                  page.update() 
             
        def on_textfield_focus(e):
            self.highlight_cell(e.control)

        
        def on_textfield_submit(e):
            # Evaluar la fórmula cuando se presiona Enter
            if e.control.value.startswith("="):
                row, col = e.control.row, e.control.col
                evaluate_formula(self, e.control.value, row, col)
                page.update()


        def on_textfield_blur(e):
            self.unhiglight_cell(e.control)
            # Evaluar la fórmula cuando la celda pierde el foco
            if e.control.value.startswith("="):
                row, col = e.control.row, e.control.col
                evaluate_formula(self, e.control.value, row, col)
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

        
        #crear filas y columnas para la tabla usando bucles
        table_rows = []
        for r in range(self.ROWS):
            row_cells = []
            for c in range(self.COLS):
                tf = ft.TextField(**textfield_style)
                tf.row, tf.col = r, c
                self.cells[r][c] = tf
                row_cells.append(tf) 
            table_rows.append(ft.Row(row_cells, spacing=0)) 

        
        table = ft.Column(table_rows, spacing=0)

        return table