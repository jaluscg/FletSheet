import re

def get_cell_value(cells, cell_ref):
    col = ord(cell_ref[0]) - 65  # Convertir A, B, C, ... a 0, 1, 2, ...
    row = int(cell_ref[1:]) - 1
    return float(cells[row][col].value)

def evaluate_formula(cells, formula, row, col):

    # Fórmula =SUM(A1, A2, ...)
    match_sum = re.match(r"=SUM\((?P<args>[A-Z]\d(?:,[A-Z]\d)*)\)", formula)
    if match_sum:
        args = match_sum.group('args').split(',')
        
        # Uso de get_cell_value
        result = 0
        for cell_ref in args:
            result += get_cell_value(cells, cell_ref)
        
        cells[row][col].value = str(result)
        return

    # Fórmula =ADD(A1,5,A2,...)
    match_add = re.match(r"=ADD\((?P<args>[A-Z]\d|[\d.]+(?:,[A-Z]\d|[\d.]+)*)\)", formula)
    if match_add:
        args = match_add.group('args').split(',')
        
        # Uso de get_cell_value
        result = 0
        for arg in args:
            if re.match(r"^[A-Z]\d$", arg):  # Si el argumento es una referencia de celda
                result += get_cell_value(cells, arg)
            else:  # Si el argumento es un número
                result += float(arg)

        cells[row][col].value = str(result)
        return

    # Fórmula general que puede contener operaciones y referencias a celdas
    def replace_cell_reference(match):
        r = int(match.group(2)) - 1
        c = ord(match.group(1)) - 65
        return str(cells[r][c].value)
    
    formula_eval = re.sub(r'([A-Z])(\d+)', replace_cell_reference, formula[1:])  # Usamos [1:] para omitir el signo "=" al principio

    try:
        result = eval(formula_eval)
        cells[row][col].value = str(result)
    except Exception as e:
        cells[row][col].value = "Error"
