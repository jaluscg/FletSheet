def column_to_index(column_name):
    """Convierte un nombre de columna Excel (e.g., 'A', 'Z', 'AA') a un índice numérico (0-based)."""
    column_name = column_name.upper()
    index = 0
    for char in column_name:
        index = index * 26 + (ord(char) - ord('A') + 1)
    print(f"Converting column {column_name} to index {index - 1}")
    return index - 1

def extract_sheet_name(range_with_sheet, current_sheet_name):
    """Extrae el nombre de la hoja de un rango dado que incluye el nombre de la hoja."""
    if '!' in range_with_sheet:
        sheet_name, _ = range_with_sheet.split('!')
        sheet_name = sheet_name.strip("'")
        return sheet_name
    return current_sheet_name

def get_criteria_value(criteria_ref, excel_data, current_sheet_name):
    """Obtiene el valor real del criterio si es una referencia de celda."""
    if criteria_ref[0].isalpha() and criteria_ref[1:].isdigit():
        col_name = ''.join(filter(str.isalpha, criteria_ref))
        row_index = int(''.join(filter(str.isdigit, criteria_ref))) - 1
        col_index = column_to_index(col_name)
        criteria_sheet_data = excel_data.get(current_sheet_name, [])
        if 0 <= row_index < len(criteria_sheet_data):
            return str(criteria_sheet_data[row_index][col_index])
    return criteria_ref

def sumifs_formula(cells, sum_range, criteria_range, criteria_ref, access_type, excel_data, current_sheet_name):
    total_sum = 0.0
    criteria = get_criteria_value(criteria_ref, excel_data, current_sheet_name)
    
    if access_type == "withexceldata" and excel_data:
        sum_sheet_name = extract_sheet_name(sum_range, current_sheet_name)
        sum_range_col = sum_range.split('!')[1] if '!' in sum_range else sum_range
        sum_range_col = sum_range_col.strip().split(':')[0]
        sum_col_index = column_to_index(sum_range_col)
        print(f"Sum sheet: {sum_sheet_name}, Sum column: {sum_range_col} (index {sum_col_index})")
        
        crit_sheet_name = extract_sheet_name(criteria_range, current_sheet_name)
        crit_range_col = criteria_range.split('!')[1] if '!' in criteria_range else criteria_range
        crit_range_col = crit_range_col.strip().split(':')[0]
        crit_col_index = column_to_index(crit_range_col)
        print(f"Criteria sheet: {crit_sheet_name}, Criteria column: {crit_range_col} (index {crit_col_index})")
        print(f"Actual criteria value used for matching: {criteria}")
        
        sum_sheet_data = excel_data.get(sum_sheet_name, [])
        crit_sheet_data = excel_data.get(crit_sheet_name, [])
        print(f"Loaded {len(sum_sheet_data)} rows from '{sum_sheet_name}' for summing.")
        print(f"Loaded {len(crit_sheet_data)} rows from '{crit_sheet_name}' for criteria checking.")
        
        for row_index in range(len(crit_sheet_data)):
            try:
                crit_value = crit_sheet_data[row_index][crit_col_index]
                print(f"Row {row_index + 1}: Checking criteria '{crit_value}' against '{criteria}'")
                if str(crit_value).strip() == str(criteria).strip():
                    sum_value = sum_sheet_data[row_index][sum_col_index]
                    if sum_value is not None and sum_value != "":
                        print(f"Row {row_index + 1}: Criteria match. Summing value: {sum_value}")
                        total_sum += float(sum_value)
            except (IndexError, ValueError) as e:
                print(f"Error at row {row_index + 1}: {e}")
    
    print(f"Final total sum: {total_sum}")
    return total_sum
