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
