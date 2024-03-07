import re
import datetime


class Formulas():
    """
    Conjunto de formulas para evaluar en la matriz de celdas
    """

    def __init__(self):
        self.excel_data = None

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

      

    def get_cell_value(self, cells, cell_ref, access_type):
            col = ord(cell_ref[0]) - 65
            row = int(cell_ref[1:]) - 1

            # Decide entre 'withexceldata' y otros modos aquí directamente
            if access_type == "withexceldata" and self.excel_data is not None:
                return self.get_cell_value_from_excel_formulas(cell_ref)
            else:
                # Lógica para 'withcell' y 'withdictionary'
                if access_type == "withcell":
                    # Acceso directo a la celda, retorna el valor tal como está
                    return cells[row][col].content.value
                elif access_type == "withdictionary":
                    # Acceso a través del diccionario, retorna el valor tal como está
                    return cells[row][col]

                # Intenta convertir el valor a un objeto datetime si parece una fecha
                if isinstance(cells[row][col], str):
                    try:
                        return datetime.datetime.strptime(cells[row][col], "%Y-%m-%dT%H:%M:%S")
                    except ValueError:
                        # Si no es una fecha, retorna el valor tal cual
                        return cells[row][col]
                else:
                    return cells[row][col]
        
    def get_cell_value_from_excel_formulas(self, cell_ref):
            col = ord(cell_ref[0]) - 65
            row = int(cell_ref[1:]) - 1
            value = self.excel_data[row][col]
            print(f"col:{col}")
            print(f"row:{row}")
            print(f"value:{value}")
                
            return value

    def evaluate_formula(self, cells, formula, row, col, access_type, excel_data=None):

        self.excel_data = excel_data

        # Si la fórmula es TEXTO para obtener el día de la semana
        if formula.startswith("=TEXT"):
            print("Se va a hacer una formula")


            if access_type == "withexceldata":
                print("Se va a hacer una formula con withexceldata")
                cell_ref_formula = formula.split('(')[1].split(';')[0]  # Extrae la referencia de la celda
                cell_ref = cell_ref_formula.strip("=TEXT()\"")  # Limpia la referencia
                print(cell_ref)
                date_str = self.get_cell_value(cells, cell_ref, access_type)  # Obtiene el valor de la celda
                print(f"date_str: {date_str}")

            else: 
                match = re.match(r'=TEXT\((?P<cell_ref>[A-Z]+\d+); ?"dddd"\)', formula)
                # Verificar si se encontró una coincidencia
                if match is not None:
                    cell_ref = match.group('cell_ref')
                    print(cell_ref)
                    date_str = self.get_cell_value(cells, cell_ref, access_type)  # Obtener el valor de la celda
                    print(f"date_str:{date_str}")
                    
            # Convertir la cadena de fecha en objeto datetime
            date_obj = datetime.datetime.strptime(date_str, "%d-%B-%Y")
            print(f"date_objet: {date_obj}")
                    
                    # Obtener el día de la semana en inglés
            day_name_english = date_obj.strftime('%A')

            print(f"day_name_english:{day_name_english}")
                    
                    # Traducir el día de la semana al español
            day_name_spanish = self.day_names_spanish.get(day_name_english, "Día desconocido")
                    
            cells[row][col].content.value = day_name_spanish
            print(f"day_name_spanish{day_name_spanish}")
            return day_name_spanish
        
        
                
        else:
            # Para otras fórmulas, utilizamos eval para una evaluación general
            def replace_cell_reference(match):
                cell_ref = match.group(0)
                return str(self.get_cell_value(cells, cell_ref, access_type))
            
            formula_eval = re.sub(r'([A-Z])(\d+)', replace_cell_reference, formula[1:])
            try:
                result = eval(formula_eval)
                if access_type == "withcell":
                    cells[row][col].content.value = result
                elif access_type == "withdictionary":
                    cells[row][col] = result
                elif access_type == "withexceldata":
                    cells[row][col] = result
                return result
            except Exception as e:
                print(f"Error evaluando la fórmula: {e}")
                # Aquí manejar el error asignando "Error" o similar a la celda afectada