import re
import datetime
import locale

# Mapeo de los días de la semana de inglés a español
day_names_spanish = {
    'Monday': 'lunes',
    'Tuesday': 'martes',
    'Wednesday': 'miércoles',
    'Thursday': 'jueves',
    'Friday': 'viernes',
    'Saturday': 'sábado',
    'Sunday': 'domingo',
}

    
def get_cell_value(cells, cell_ref, access_type):
    col = ord(cell_ref[0]) - 65
    row = int(cell_ref[1:]) - 1
    value = None

    if access_type == "withcell":
        # Acceso directo a la celda, retorna el valor tal como está
        value = cells[row][col].content.value
    elif access_type == "withdictionary":
        # Acceso a través del diccionario, retorna el valor tal como está
        value = cells[row][col]
    elif access_type == "withexceldata":
        # Acceso directo a la celda desde excel_data
        value = cells[row][col]

    # Intenta convertir el valor a un objeto datetime si parece una fecha
    if isinstance(value, str):
        try:
            return datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M:%S")
        except ValueError:
            # Si no es una fecha, retorna el valor tal cual
            return value
    else:
        return value   

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

    # Si la fórmula es TEXTO para obtener el día de la semana
    elif formula.startswith("=TEXT"):
        match = re.match(r'=TEXT\((?P<cell_ref>[A-Z]\d); ?"dddd"\)', formula)
        if match:
            cell_ref = match.group('cell_ref')
            print(cell_ref)
            date_str = get_cell_value(cells, cell_ref, access_type)  # Obtener el valor de la celda
            print(f"date_str:{date_str}")
            
            # Convertir la cadena de fecha en objeto datetime
            date_obj = datetime.datetime.strptime(date_str, "%d-%B-%Y")
            print(f"date_objet: {date_obj}")
            
            # Obtener el día de la semana en inglés
            day_name_english = date_obj.strftime('%A')

            print(f"day_name_english:{day_name_english}")
            
            # Traducir el día de la semana al español
            day_name_spanish = day_names_spanish.get(day_name_english, "Día desconocido")
            
            cells[row][col].content.value = day_name_spanish
            print(f"day_name_spanish{day_name_spanish}")
            return day_name_spanish
    
        
    def get_cell_value_from_excel(excel_data, cell_ref):
        col = ord(cell_ref[0]) - 65
        row = int(cell_ref[1:]) - 1
        value = excel_data[row][col]
        
        return value


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