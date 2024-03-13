def sum_formula(cells, cell_range, excel_data=None):
    total_sum = 0.0
    start_cell, end_cell = cell_range.split(':')
    start_col, start_row = ord(start_cell[0]) - 65, int(start_cell[1:]) - 1
    end_col, end_row = ord(end_cell[0]) - 65, int(end_cell[1:]) - 1

    for row in range(start_row, end_row + 1):
        for col in range(start_col, end_col + 1):
            cell_value = 0
            if excel_data and row < len(excel_data) and col < len(excel_data[row]):
                #print(f"start_cell: {start_cell}, end_cell: {end_cell}, start_col: {start_col}, start_row:{start_row}, end_col:{end_col}, end_row: {end_row}")
                #print(f"valor excel data: {excel_data[row][col]}")
                cell_value = excel_data[row][col] if excel_data[row][col] is not None else 0
                source = "excel_data"
            elif row < len(cells) and col < len(cells[row]):
                cell_value = cells[row][col].content.value if hasattr(cells[row][col], 'content') else cells[row][col]
                source = "visible cells"
            else:
                source = "default"

            print(f"Accediendo a [{row}, {col}] desde {source}, valor = {cell_value}")
            try:
                total_sum += float(cell_value)
            except ValueError:
                print(f"El valor '{cell_value}' en [{row}, {col}] no es numérico y se ignorará.")

    if total_sum.is_integer():
        return int(total_sum)
    else:
        return total_sum
