def sumifs_formula(cells, sum_range, criteria_ranges, criteria_values, access_type, excel_data=None, current_sheet_name=None):
    total_sum = 0.0
    print("Debug - En sumifs formula")
    
    # Asegurar el manejo de rangos de una sola columna para sum_range como 'I:I'
    if ':' in sum_range:
        start_col_index_sum, end_col_index_sum = ord(sum_range[0].upper()) - 65, ord(sum_range[0].upper()) - 65
        start_row_sum, end_row_sum = 0, float('inf')  # Asumir todo el rango de la columna
    else:
        start_col_index_sum, end_col_index_sum = ord(sum_range[0].upper()) - 65, ord(sum_range[0].upper()) - 65
        start_row_sum = int(sum_range[1:]) - 1
        end_row_sum = start_row_sum

    print(f"Debug - Rango de suma: {sum_range}, Índices de columna: {start_col_index_sum} a {end_col_index_sum}, Filas: {start_row_sum} a {end_row_sum}")

    if access_type == "withexceldata" and excel_data and current_sheet_name:
        sheet_data = excel_data.get(current_sheet_name, [])
        max_row = len(sheet_data)
        # Ajuste para el caso de 'inf' en end_row_sum
        end_row_sum = min(end_row_sum, max_row - 1)
        print("Debug - Procesando con excel_data...")

        for row in range(start_row_sum, end_row_sum + 1):
            include_sum = True
            for crit_range, crit_value in zip(criteria_ranges, criteria_values):
                crit_sheet, crit_col_range = crit_range.split('!') if '!' in crit_range else (current_sheet_name, crit_range)
                crit_col_index = ord(crit_col_range[0].upper()) - 65
                
                # Seleccionar la hoja correcta para el criterio
                crit_sheet_data = excel_data.get(crit_sheet, [])
                
                cell_value = crit_sheet_data[row][crit_col_index] if row < len(crit_sheet_data) and crit_col_index < len(crit_sheet_data[row]) else None
                print(f"Debug - Rango de criterio: {crit_range}, valor de criterio: {crit_value}, Valor de celda: {cell_value}, Comparación: {cell_value} != {crit_value}")
                
                if str(cell_value).strip() != str(crit_value).strip():
                    include_sum = False
                    break

            if include_sum:
                for col in range(start_col_index_sum, end_col_index_sum + 1):
                    try:
                        cell_value = sheet_data[row][col] if row < len(sheet_data) and col < len(sheet_data[row]) else 0
                        print(f"Debug - Valor de celda para sumar: {cell_value}, en fila {row}, columna {col}")
                        if cell_value is not None:
                            total_sum += float(cell_value)
                    except ValueError:
                        print(f"Debug - El valor '{cell_value}' en fila {row}, columna {col} no es numérico y se ignorará.")

    # Repetir una lógica similar para el caso "withcell" si es necesario
    # Ajuste final para total_sum (para manejar .0)
    return int(total_sum) if total_sum.is_integer() else total_sum
