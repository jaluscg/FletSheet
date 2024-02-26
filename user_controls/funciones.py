import re


def get_cell_value(cells, cell_ref, access_type):
    col = ord(cell_ref[0]) - 65
    row = int(cell_ref[1:]) - 1
    if access_type == "withcell":
        # Acceso directo a la celda
        try:
            return float(cells[row][col].content.value)
        except ValueError:
            return 0
    elif access_type == "withdictionary":
        # Acceso a través del diccionario
        try:
            return float(cells[row][col])
        except ValueError:
            return 0
        
    if access_type == "withexceldata":
        # Acceso directo a la celda
        try:
            return float(cells[row][col]) and print (f"float(cells[row][col]){float(cells[row][col])}")
        except ValueError:
            return 0 and print (f"row{row}, col{col}")
   

def evaluate_formula(cells, formula, row, col, access_type, excel_data=None):
    # Identificar la fórmula utilizada
    if formula.startswith("=SUM"):
        
        match = re.match(r"=SUM\((?P<args>[A-Z]\d(?:,[A-Z]\d)*)\)", formula)
        if match:
            args = match.group('args').split(',')
            result = sum([get_cell_value(cells, cell_ref, access_type) for cell_ref in args])
            cells[row][col].content.value = str(result)
            print(f"SUM Result: {result}")  # Para diagnóstico
            return result
    def get_cell_value_from_excel(excel_data, cell_ref):
        col = ord(cell_ref[0]) - 65
        row = int(cell_ref[1:]) - 1
        try:
            return float(excel_data[row][col])
        except (ValueError, IndexError):
            return 0
    
    # Para fórmulas generales que pueden contener operaciones y referencias a celdas
    def replace_cell_reference(match):
        r = int(match.group(2)) - 1
        c = ord(match.group(1)) - 65
        if access_type == "withcell":
            return str(cells[r][c].content.value)
        elif access_type == "withdictionary":
            return str(cells[r][c])
        elif access_type == "withexceldata":
            if excel_data:
                return str(get_cell_value_from_excel(excel_data, match.group()))
            else:
                # Manejo cuando excel_data no está disponible
                return "0" # O alguna otra lógica adecuada

    formula_eval = re.sub(r'([A-Z])(\d+)', replace_cell_reference, formula[1:])
    # ...

    try:
        result = eval(formula_eval)
        return result
    
    except Exception as e:
        if access_type == "withcell":
            cells[row][col].content.value = "Error"
        elif access_type == "withdictionary":
            cells[row][col] = "Error"
        elif access_type == "withexceldata":
            cells[row][col] = "Error"