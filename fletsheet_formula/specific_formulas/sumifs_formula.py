def column_to_index(column_name):
    """Convierte un nombre de columna Excel (e.g., 'A', 'Z', 'AA') a un índice numérico (0-based)."""
    column_name = column_name.upper()
    index = 0
    for char in column_name:
        index = index * 26 + (ord(char) - ord('A') + 1)
    print(f"Converting column {column_name} to index {index - 1}")
    return index - 1

def extract_sheet_name(range_with_sheet):
    """Extrae el nombre de la hoja de un rango dado que incluye el nombre de la hoja."""
    if '!' in range_with_sheet:
        sheet_name, _ = range_with_sheet.split('!')
        # Eliminar comillas simples que rodean el nombre de la hoja si están presentes
        sheet_name = sheet_name.strip("'")
        return sheet_name
    return None

def sumifs_formula(cells, sum_range, criteria_range, criteria, access_type, excel_data, current_sheet_name):
    total_sum = 0.0
    
    if access_type == "withexceldata" and excel_data:
        # Extraer y procesar el nombre de la hoja y columna del rango de suma
        sum_sheet_name = extract_sheet_name(sum_range)
        sum_range_col = sum_range.split('!')[1] if '!' in sum_range else sum_range
        sum_range_col = sum_range_col.strip().split(':')[0]
        sum_col_index = column_to_index(sum_range_col)
        print(f"Sum sheet: {sum_sheet_name}, Sum column: {sum_range_col} (index {sum_col_index})")
        
        # Extraer y procesar el nombre de la hoja y columna del rango de criterios
        crit_sheet_name = extract_sheet_name(criteria_range)
        crit_range_col = criteria_range.split('!')[1] if '!' in criteria_range else criteria_range
        crit_range_col = crit_range_col.strip().split(':')[0]
        crit_col_index = column_to_index(crit_range_col)
        print(f"Criteria sheet: {crit_sheet_name}, Criteria column: {crit_range_col} (index {crit_col_index})")
        
        # Acceder a los datos de las hojas
        sum_sheet_data = excel_data.get(sum_sheet_name, [])
        crit_sheet_data = excel_data.get(crit_sheet_name, [])
        print(f"Loaded {len(sum_sheet_data)} rows from '{sum_sheet_name}' for summing.")
        print(f"Loaded {len(crit_sheet_data)} rows from '{crit_sheet_name}' for criteria checking.")
        
        # Proceso de sumifs
        for row_index in range(1, len(crit_sheet_data)):  # Start at 1 to skip header row
            try:
                crit_value = crit_sheet_data[row_index][crit_col_index]
                print(f"Row {row_index}: Criteria value = {crit_value}")
                if str(crit_value).strip() == str(criteria).strip():
                    sum_value = sum_sheet_data[row_index][sum_col_index]
                    print(f"Row {row_index}: Sum value = {sum_value}")
                    if sum_value is not None and sum_value != "":
                        total_sum += float(sum_value)
            except (IndexError, ValueError) as e:
                print(f"Error at row {row_index}: {e}")
                continue  # Manejar índices fuera de rango y conversiones fallidas

    print(f"Total sum: {total_sum}")
    return total_sum
