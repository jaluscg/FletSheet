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


 
    def load_excel_data(self, filepath):
        workbook = openpyxl.load_workbook(filepath, data_only=True)
        data = {}
        for sheet in workbook.sheetnames:
            worksheet = workbook[sheet]
            data[sheet] = [[cell.value for cell in row] for row in worksheet.iter_rows()]
        return data

    def on_keyboard_event(self, e:ft.KeyboardEvent, page):

        def almacenar_datoescrito():
        # Obtener el nombre de la hoja actual

            sheet_name = self.current_sheet 

            # Asegurarse de que haya un diccionario para la hoja actual en self.edited_cells
            if sheet_name not in self.edited_cells:
                self.edited_cells[sheet_name] = {}

            # Actualizar el registro de cambios con el nuevo valor
            self.edited_cells[sheet_name][(current_row, current_col)] = current_cell.content.value

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
                
            almacenar_datoescrito()

            page.update()

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






    def update_visible_cells(self):
        # Verificar si se está utilizando btn_hoja y configurar el nombre de la hoja
        sheet_name = self.current_sheet if not self.btn_hoja else self.current_sheet

        for r in range(self.ROWS):
            for c in range(self.COLS):
                # Calcular la posición real de la celda en los datos
                data_row = r + self.visible_start_row
                data_col = c + self.visible_start_col

                # Comprobar si la celda ha sido editada
                if (data_row, data_col) in self.edited_cells:
                    # Si la celda ha sido editada, usar el valor editado
                    cell_value = self.edited_cells[(data_row, data_col)]
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