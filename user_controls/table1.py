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


from typing import Any, List, Optional, Union
from flet_core.constrained_control import ConstrainedControl
from flet_core.control import Control, OptionalNumber
from flet_core.ref import Ref
from flet_core.types import (
    AnimationValue,
    OffsetValue,
    PaddingValue,
    ResponsiveNumber,
    RotateValue,
    ScaleValue,
)


class TextFieldTable(ConstrainedControl, SpecificScrollableControl):
    """
    Una matriz de celdas que se puede editar y desplazar.
    """
    def __init__(
        self,
        rows,
        cols,
        cell_height: OptionalNumber = 30,
        cell_width: OptionalNumber = 100,
        controls: Optional[List[Control]] = None,
        ref: Optional[Ref] = None,
        key: Optional[str] = None,
        width: OptionalNumber = None,
        height: OptionalNumber = None,
        left: OptionalNumber = None,
        top: OptionalNumber = None,
        right: OptionalNumber = None,
        bottom: OptionalNumber = None,
        expand: Union[None, bool, int] = None,
        col: Optional[ResponsiveNumber] = None,
        opacity: OptionalNumber = None,
        rotate: RotateValue = None,
        scale: ScaleValue = None,
        offset: OffsetValue = None,
        aspect_ratio: OptionalNumber = None,
        animate_opacity: AnimationValue = None,
        animate_size: AnimationValue = None,
        animate_position: AnimationValue = None,
        animate_rotation: AnimationValue = None,
        animate_scale: AnimationValue = None,
        animate_offset: AnimationValue = None,
        on_animation_end=None,
        visible: Optional[bool] = None,
        disabled: Optional[bool] = None,
        data: Any = None,
        #
        # ScrollableControl specific
        #
        auto_scroll: Optional[bool] = None,
        reverse: Optional[bool] = None,
        on_scroll_interval: OptionalNumber = None,
        on_scroll: Any = None,
        #
        # Specific
        #
        horizontal: Optional[bool] = None,
        spacing: OptionalNumber = None,
        item_extent: OptionalNumber = None,
        first_item_prototype: Optional[bool] = None,
        divider_thickness: OptionalNumber = None,
        padding: PaddingValue = None,
    ):
        ConstrainedControl.__init__(
            self,
            ref=ref,
            key=key,
            width=width,
            height=height,
            left=left,
            top=top,
            right=right,
            bottom=bottom,
            expand=expand,
            col=col,
            opacity=opacity,
            rotate=rotate,
            scale=scale,
            offset=offset,
            aspect_ratio=aspect_ratio,
            animate_opacity=animate_opacity,
            animate_size=animate_size,
            animate_position=animate_position,
            animate_rotation=animate_rotation,
            animate_scale=animate_scale,
            animate_offset=animate_offset,
            on_animation_end=on_animation_end,
            visible=visible,
            disabled=disabled,
            data=data,
        )

        SpecificScrollableControl.__init__(
            self,
            auto_scroll=auto_scroll,
            reverse=reverse,
            on_scroll_interval=on_scroll_interval,
            on_scroll=on_scroll,
        )

        self.__controls: List[Control] = []
        self.controls = controls
        self.horizontal = horizontal
        self.spacing = spacing
        self.divider_thickness = divider_thickness
        self.item_extent = item_extent
        self.first_item_prototype = first_item_prototype
        self.padding = padding
    
        
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
                    #on_pan_start=lambda e: None if self.is_mobile_device(page) or self.is_packege_device(page) else self.on_pan_start(e, page),
                    #on_pan_update=lambda e: None if self.is_mobile_device(page) or self.is_packege_device(page) else self.on_pan_update(e, page),
                    #on_pan_end=lambda e: None if self.is_mobile_device(page) or self.is_packege_device(page) else self.on_pan_end(e, page),
                    on_tap=lambda e: self.on_single_click(e, page),
                    on_double_tap=lambda e: self.on_double_click(e, page),
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
        
        inicio_tabla = Column(self.table_rows, spacing=0)

        # Crear una columna con todas las filas para permitir desplazamiento vertical
        #vertical_scroll = SpecificColumn([column_indices, inicio_tabla],  spacing=0, scroll=ft.ScrollMode.ALWAYS, height=page.height /3)
        vertical_scroll = SpecificColumn([inicio_tabla],  spacing=0, scroll=ft.ScrollMode.ALWAYS, height=page.height /3)

        # Envolver la columna en un contenedor Row para desplazamiento horizontal
        #scrollable_columns = SpecificRow([row_indices, vertical_scroll], spacing=0, scroll=ft.ScrollMode.ALWAYS,alignment=MainAxisAlignment.START, vertical_alignment=CrossAxisAlignment.START,width= page.width / 2 )
        scrollable_columns = SpecificRow([vertical_scroll], spacing=0, scroll=ft.ScrollMode.ALWAYS,alignment=MainAxisAlignment.START, vertical_alignment=CrossAxisAlignment.START,width= page.width / 2 )

        seccion_hojas = self.create_sheets_section(page)

        final_table = ft.Column([
                scrollable_columns,           
                seccion_hojas,
                
        ])
        

        return final_table