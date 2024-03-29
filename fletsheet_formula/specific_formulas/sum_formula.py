def sum_formula(cells, cell_range, access_type, excel_data=None, current_sheet_name=None):
    total_sum = 0.0
    start_cell, end_cell = cell_range.split(':')
    start_col_index, start_row = ord(start_cell[0].upper()) - 65, int(start_cell[1:]) - 1
    end_col_index, end_row = ord(end_cell[0].upper()) - 65, int(end_cell[1:]) - 1
    
    
    if access_type == "withexceldata" and excel_data and current_sheet_name:
        
        sheet_data = excel_data.get(current_sheet_name, [])

        for row in range(start_row, end_row + 1):
            for col in range(start_col_index, end_col_index + 1):
                try:
                    cell_value = sheet_data[row][col] if row < len(sheet_data) and col < len(sheet_data[row]) else 0
                    print(f"Valor de la celda [{row + 1}, {col + 1}]: {cell_value}")
                    # Comprobar si el valor de la celda es None antes de sumar
                    if cell_value is not None:
                        total_sum += float(cell_value)
                        print(f"Suma parcial: {total_sum}")
                    else:
                        print(f"Valor None encontrado en la fila {row + 1}, columna {col + 1}, tratado como 0.")
                except ValueError:
                    print(f"El valor '{cell_value}' en [{row + 1}, {col + 1}] no es numérico y se ignorará.")
                except IndexError:
                    print(f"Índice fuera de rango en excel_data: [{row + 1}, {col + 1}]")


    elif access_type == "withcell":
        total_sum = 0.0  # Inicializar total_sum como flotante
        start_cell, end_cell = cell_range.split(':')
        start_col, start_row = ord(start_cell[0]) - 65, int(start_cell[1:]) - 1
        end_col, end_row = ord(end_cell[0]) - 65, int(end_cell[1:]) - 1
        start_col, start_row = ord(start_cell[0]) - 65, int(start_cell[1:]) - 1
    
        for row in range(start_row, end_row + 1):
            for col in range(start_col, end_col + 1):
                cell_value = cells[row][col].content.value if hasattr(cells[row][col], 'content') else cells[row][col]
                # Verificar si el valor es None antes de intentar convertir a float
                if cell_value is not None:
                    try:
                        total_sum += float(cell_value)
                    except ValueError:
                        # Maneja la excepción si la conversión falla
                        print(f"No se puede convertir el valor de la celda {chr(col + 65)}{row + 1} a número.")
                else:
                    print(f"0")

        # Ajuste para evitar el .0 en números enteros
    if total_sum.is_integer():
        return int(total_sum)
    else:
        return total_sum
