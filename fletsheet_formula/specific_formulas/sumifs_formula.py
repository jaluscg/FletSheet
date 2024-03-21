def sumifs_formula(cells, sum_range, criteria_range, criteria, current_sheet_name=None):
    total_sum = 0.0

    # Obtiene los nombres de las hojas y rangos o celdas de criterios
    sum_sheet, sum_range = sum_range.split('!') if '!' in sum_range else (current_sheet_name, sum_range)
    criteria_sheet, criteria_range = criteria_range.split('!') if '!' in criteria_range else (current_sheet_name, criteria_range)
    criteria_sheet, criteria_cell = criteria.split('!') if '!' in criteria else (criteria_sheet, criteria)

    # Calcula las posiciones de columna para la suma y los criterios
    sum_col = ord(sum_range[0]) - 65
    criteria_col = ord(criteria_range[0]) - 65
    criteria_row = int(criteria_cell[1:]) - 1

    # Obtiene el valor del criterio
    if access_type == "withexceldata":
        criteria_value = excel_data[criteria_sheet][criteria_row][criteria_col] if criteria_row < len(excel_data.get(criteria_sheet, [])) else None
        print(f"Valor del criterio: {criteria_value}")
        if criteria_value is not None:
            # Itera sobre cada fila en el rango de suma
            for row in excel_data.get(sum_sheet, []):
                cell_value = row[sum_col] if sum_col < len(row) else 0
                print(f"Valor de la celda: {cell_value}")
                # Compara el valor de la celda en el rango de criterio con el valor de criterio
                if row[criteria_col] == criteria_value:
                    try:
                        total_sum += float(cell_value)
                    except ValueError:
                        pass  # Ignora los valores no numéricos

    elif access_type == "withcell":
        criteria_value = None
        # Suponiendo que las celdas es una lista de listas con objetos de celda
        for row in cells:
            for cell in row:
                if cell.row == criteria_row and cell.col == criteria_col:
                    criteria_value = cell.value
                    break
            if criteria_value:
                break

        if criteria_value:
            for row in cells:
                for cell in row:
                    if cell.col == sum_col and cell.value == criteria_value:
                        try:
                            total_sum += float(cell.value)
                        except ValueError:
                            pass  # Omitir valores no numéricos

    return total_sum
