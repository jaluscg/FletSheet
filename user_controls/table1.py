import flet as ft
from flet import *
import re
from .funciones import evaluate_formula
import openpyxl



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
        self.excel_data = self.load_excel_data("./assets/contabilizacion.xlsx")
        self.cell_height = cell_height  
        self.cell_width = cell_width
        self.current_sheet = next(iter(self.excel_data), None) 
        self.btn_hoja = False
        self.edited_cells = {}  

    def on_keyboard_event(self, e:ft.KeyboardEvent, page):
        def almacenar_datoescrito(current_row, current_col, current_cell):
            # Ajustar las coordenadas de la celda a la posición de desplazamiento
            adjusted_row = current_row + self.visible_start_row 
            adjusted_col = current_col + self.visible_start_col 

            sheet_name = self.current_sheet 
            if sheet_name not in self.edited_cells:
                self.edited_cells[sheet_name] = {}
            self.edited_cells[sheet_name][(adjusted_row, adjusted_col)] = current_cell.content.value

            print(self.edited_cells)
        
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
                
            almacenar_datoescrito(current_row, current_col, current_cell)

            page.update()

    
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
                                    current_cell.content.value = value
                                    almacenar_datoescrito(row, col, current_cell)  # Actualizar self.edited_cells
                                    if value.startswith("="):  # Si es una fórmula
                                        evaluate_formula(self.cells, value, row, col)  # Evaluar fórmulas         

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



 
    def load_excel_data(self, filepath):
        workbook = openpyxl.load_workbook(filepath, data_only=True)
        data = {}
        for sheet in workbook.sheetnames:
            worksheet = workbook[sheet]
            data[sheet] = [[cell.value for cell in row] for row in worksheet.iter_rows()]
        return data
    
    





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
                    on_pan_start=lambda e: self.on_pan_start(e, page),
                    on_pan_update=lambda e: self.on_pan_update(e, page),
                    on_pan_end=lambda e: self.on_pan_end(e, page),
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