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
        
        #super().__init__()
        
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
        self.visible_start_row = 0
        self.visible_end_row = 12  if rows < 12 else rows
        self.visible_start_col = 0
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




    

    def handle_scroll(self, e, page):
        # Calcular los índices de fila y columna basándose en el desplazamiento del scroll
        delta_rows = int(e.scroll_delta_y / self.cell_height)
        delta_cols = int(e.scroll_delta_x / self.cell_width)

        self.visible_start_row = max(0, self.visible_start_row + delta_rows)
        self.visible_start_col = max(0, self.visible_start_col + delta_cols)



        # Actualizar celdas visibles
        self.update_visible_cells()

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
        sheet_name = 'historialdecont'  # Asumiendo que quieres mostrar esta hoja
        for r in range(self.ROWS):
            for c in range(self.COLS):
                data_row = r + self.visible_start_row
                data_col = c + self.visible_start_col

                if sheet_name in self.excel_data and data_row < len(self.excel_data[sheet_name]) and data_col < len(self.excel_data[sheet_name][data_row]):
                    cell_value = self.excel_data[sheet_name][data_row][data_col]
                else:
                    cell_value = ""

                self.cells[r][c].content.value = str(cell_value) 

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
                    on_scroll= lambda e: self.handle_scroll(e, page)
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
        scrollable_columns.on_scroll = self.handle_scroll

        # Añadir un contenedor que se desplazará verticalmente y contendrá los índices de las filas y el contenedor anterior
        scrollable_with_row_indices = ft.Column(
            [column_indices, scrollable_columns],
            spacing=0,
            scroll=ft.ScrollMode.ALWAYS,
            height=self.cell_height * (self.visible_end_row )  # +1 para incluir el espacio de los índices de columna
        )

        final_table_container = ft.Row(
            [scrollable_with_row_indices],
            spacing=0,
            scroll=ft.ScrollMode.ALWAYS,
            width=self.cell_width * (self.visible_end_col) +30
        )

       

        return final_table_container