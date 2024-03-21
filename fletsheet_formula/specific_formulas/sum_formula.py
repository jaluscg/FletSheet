def sum_formula(cells, cell_range):
    total_sum = 0.0  # Inicializar total_sum como flotante
    # Descomponer el rango en celda inicial y final
    start_cell, end_cell = cell_range.split(':')
    start_col, start_row = ord(start_cell[0]) - 65, int(start_cell[1:]) - 1
    end_col, end_row = ord(end_cell[0]) - 65, int(end_cell[1:]) - 1


    # Iterar a través del rango de celdas
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
