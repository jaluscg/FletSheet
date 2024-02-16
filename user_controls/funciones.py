import re

def get_cell_value(cells, cell_ref):
    col = ord(cell_ref[0]) - 65  # Convertir A, B, C, ... a 0, 1, 2, ...
    row = int(cell_ref[1:]) - 1
    try:
        # Asegurarse de que el valor es numérico; de lo contrario, devolver 0
        return float(cells[row][col].content.value)
    except ValueError:
        return 0

def evaluate_formula(cells, formula, row, col):
    # Identificar la fórmula utilizada
    if formula.startswith("=SUM"):
        
        match = re.match(r"=SUM\((?P<args>[A-Z]\d(?:,[A-Z]\d)*)\)", formula)
        if match:
            args = match.group('args').split(',')
            result = sum([get_cell_value(cells, cell_ref) for cell_ref in args])
            cells[row][col].content.value = str(result)
            print(f"SUM Result: {result}")  # Para diagnóstico
            return result

    
    # Para fórmulas generales que pueden contener operaciones y referencias a celdas
    def replace_cell_reference(match):
        r = int(match.group(2)) - 1
        c = ord(match.group(1)) - 65
        return str(cells[r][c].content.value)
    
    formula_eval = re.sub(r'([A-Z])(\d+)', replace_cell_reference, formula[1:])  # Usamos [1:] para omitir el signo "=" al principio

    try:
        result = eval(formula_eval)
        return result
    except Exception as e:
        cells[row][col].content.value = "Error"

    
    



    