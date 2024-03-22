def column_to_index(column_name):
    """Convierte un nombre de columna Excel (e.g., 'A', 'Z', 'AA') a un índice numérico (0-based)."""
    column_name = column_name.upper()
    index = 0
    for char in column_name:
        index = index * 26 + (ord(char) - ord('A') + 1)
    print(f"Converting column {column_name} to index {index - 1}")
    return index - 1

def sumifs_formula(cells, sum_range, criteria_range, criteria, access_type, excel_data, current_sheet_name):
    total_sum = 0.0
    
    if access_type == "withexceldata" and excel_data:
        # Parse sum_range
        sum_sheet_name, sum_range_col = sum_range.split('!') if '!' in sum_range else (current_sheet_name, sum_range)
        sum_range_col = sum_range_col.strip().split(':')[0]  # Asumiendo un rango simple
        sum_col_index = column_to_index(sum_range_col)
        print(f"Sum sheet: {sum_sheet_name}, Sum column: {sum_range_col} (index {sum_col_index})")
        
        # Parse criteria_range
        crit_sheet_name, crit_range_col = criteria_range.split('!') if '!' in criteria_range else (current_sheet_name, criteria_range)
        crit_range_col = crit_range_col.strip().split(':')[0]  # Asumiendo un rango simple
        crit_col_index = column_to_index(crit_range_col)
        print(f"Criteria sheet: {crit_sheet_name}, Criteria column: {crit_range_col} (index {crit_col_index})")
        
        # Acceso a los datos de las hojas
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
