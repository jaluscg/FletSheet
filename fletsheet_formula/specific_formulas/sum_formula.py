def sum_formula(cell_values, cell_range, access_type, get_cell_value_func):
    if access_type == "withexceldata":
        # Logic to sum up values from `excel_data` based on cell_range
        start_cell, end_cell = cell_range.split(':')
        start_col = ord(start_cell[0]) - 65
        end_col = ord(end_cell[0]) - 65
        start_row = int(start_cell[1:]) - 1
        end_row = int(end_cell[1:]) - 1

        sum_result = 0
        for row in range(start_row, end_row + 1):
            for col in range(start_col, end_col + 1):
                cell_ref = chr(65 + col) + str(row + 1)
                value = get_cell_value_func(cells, cell_ref, access_type)
                try:
                    sum_result += float(value)
                except ValueError:
                    pass
        return sum_result
    else:
        # Similar logic for 'withcell' or 'withdictionary', adjusting as needed
        ...
