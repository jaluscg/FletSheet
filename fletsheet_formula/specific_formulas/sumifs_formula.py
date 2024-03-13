def sumifs_formula(cells, sum_range, criteria_range, criteria, excel_data=None):
    total_sum = 0.0
    # Descomponer las referencias de las celdas para extraer las hojas y rangos
    sum_sheet, sum_range = sum_range.split('!') if '!' in sum_range else (None, sum_range)
    criteria_sheet, criteria_range = criteria_range.split('!') if '!' in criteria_range else (None, criteria_range)
    criteria_sheet, criteria_cell = criteria.split('!') if '!' in criteria else (None, criteria)

    sum_col = ord(sum_range[0]) - 65
    criteria_col = ord(criteria_range[0]) - 65
    criteria_row = int(criteria_cell[1:]) - 1

    print(f"Procesando SUMIFS para la hoja '{sum_sheet}', rango de suma '{sum_range}', basado en el criterio de la hoja '{criteria_sheet}', rango '{criteria_range}', celda de criterio '{criteria_cell}'")

    if criteria_sheet and criteria_row < len(excel_data[criteria_sheet]):
        criteria_value = excel_data[criteria_sheet][criteria_row][criteria_col]
        print(f"Valor del criterio encontrado: {criteria_value}")
    else:
        # Fallback si no se especifica hoja o no se encuentra el valor
        criteria_value = None
        print("No se pudo encontrar el valor del criterio.")

    if sum_sheet and criteria_value is not None:
        for row in range(len(excel_data[sum_sheet])):
            cell_value = excel_data[sum_sheet][row][sum_col] if sum_col < len(excel_data[sum_sheet][row]) else 0
            if excel_data[criteria_sheet][row][criteria_col] == criteria_value:
                print(f"Añadiendo valor {cell_value} de la fila {row}, columna {sum_col} de la hoja '{sum_sheet}' al total.")
                try:
                    total_sum += float(cell_value)
                except ValueError:
                    print(f"El valor '{cell_value}' en la fila {row}, columna {sum_col} no es numérico y se ignorará.")
    else:
        print("No se realizará la suma debido a la falta del valor de criterio o problemas con el nombre de la hoja.")

    print(f"Suma total: {total_sum}")
    return total_sum
