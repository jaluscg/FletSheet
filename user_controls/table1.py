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
        self.visible_end_row = 12  if rows < 12 else rows
        self.visible_start_col = 1
        self.visible_end_col = 10  if cols < 10 else cols
        self.start_cell = None 
        self.table_rows = []
        self.table_initialized = False  # Inicializa el estado de la tabla
        self.excel_data = self.load_excel_data("./assets/contabilizacion.xlsx")
        self.cell_height = cell_height  
        self.cell_width = cell_width


 
    def load_excel_data(self, filepath):
        workbook = openpyxl.load_workbook(filepath, data_only=True)
        data = {}
        for sheet in workbook.sheetnames:
            worksheet = workbook[sheet]
            data[sheet] = [[cell.value for cell in row] for row in worksheet.iter_rows()]
        return data
    


    def handle_scroll_event(self, e, page):
        # Calcular los índices de fila y columna basándose en el desplazamiento del scroll
        delta_rows = int(e.scroll_delta_y / self.cell_height)
        delta_cols = int(e.scroll_delta_x / self.cell_width)

        self.visible_start_row = max(0, self.visible_start_row + delta_rows)
        self.visible_end_row = min(self.ROWS, self.visible_start_row + 12)
        
        self.visible_start_col = max(0, self.visible_start_col + delta_cols)
        self.visible_end_col = min(self.COLS, self.visible_start_col + 10)

        # Actualizar celdas visibles
        self.update_visible_cells()
        self.update_indices()

        # Actualizar la página para reflejar los cambios
        page.update()

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
        sheet_name = 'productos'  # Asumiendo que quieres mostrar esta hoja
        for r in range(self.ROWS):
            for c in range(self.COLS):
                data_row = r + self.visible_start_row
                data_col = c + self.visible_start_col

                if sheet_name in self.excel_data and data_row < len(self.excel_data[sheet_name]) and data_col < len(self.excel_data[sheet_name][data_row]):
                    cell_value = self.excel_data[sheet_name][data_row][data_col]
                else:
                    cell_value = ""

                self.cells[r][c].content.value = str(cell_value) 
            
    


     # Manejar evento de cambio en el slider horizontal
    def on_horizontal_slider_change(self, e, page):
        # Calcula el desplazamiento en las columnas basado en el valor del slider
        self.visible_start_col = int(e.control.value)
        self.visible_end_col = min(self.COLS, self.visible_start_col + 10)
        self.update_visible_cells()
        page.update()

    # Manejar evento de cambio en el slider vertical
    def on_vertical_slider_change(self, e, page):
        # Calcula el desplazamiento en las filas basado en el valor del slider
        self.visible_start_row = int(e.control.value)
        self.visible_end_row = min(self.ROWS, self.visible_start_row + 12)
        self.update_visible_cells()
        page.update()

    # Crear slider horizontal
    def create_horizontal_slider(self, page):
        slider = ft.Slider(
            min=0, 
            max=self.COLS - 10, 
            on_change=lambda e: self.on_horizontal_slider_change(e, page)
        )
        return slider

    # Crear slider vertical
    def create_vertical_slider(self, page):
        slider = ft.Slider(
            min=0, 
            max=self.ROWS - 12, 
            on_change=lambda e: self.on_vertical_slider_change(e, page),
            rotate= 0.9,
        )
        return slider

    
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
       
        self.table_rows= []
        for r in range(self.ROWS):
            row_cells = []
            for c in range(self.COLS):
                
                cell_content = ""
                # Inicializar con datos visibles
                if r < self.visible_end_row and c < self.visible_end_col:
                    cell_content = str(self.excel_data['productos'][r][c]) if r < len(self.excel_data['productos']) and c < len(self.excel_data['productos'][r]) else ""
                
                tf = ft.Container(**container_style, content= Text(cell_content)) 
                

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

        # Añadir barras de navegación
        horizontal_slider = self.create_horizontal_slider(page)
        vertical_slider = self.create_vertical_slider(page)
     
        final_table = ft.Column([
            ft.Row([
                tabla_indices,
                vertical_slider
            ]),
            horizontal_slider
        ])
        

        return final_table