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
                    # Comprobar si el valor de la celda es None antes de sumar
                    if cell_value is not None:
                        total_sum += float(cell_value)
                    else:
                        print(f"Valor None encontrado en la fila {row + 1}, columna {col + 1}, tratado como 0.")
                except ValueError:
                    print(f"El valor '{cell_value}' en [{row + 1}, {col + 1}] no es numérico y se ignorará.")
                except IndexError:
                    print(f"Índice fuera de rango en excel_data: [{row + 1}, {col + 1}]")

    elif access_type == "withcell":
        # El manejo similar debería aplicarse aquí si es necesario
        pass

    if total_sum.is_integer():
        return int(total_sum)
    else:
        return total_sum
