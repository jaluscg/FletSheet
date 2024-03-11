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

    def extract_cell_reference(self, formula):
        # Busca el inicio de la referencia de la celda después del primer paréntesis
        start_index = formula.find('(') + 1
        # Busca el final de la referencia de la celda, que sería la primera coma o paréntesis de cierre
        end_index = formula.find(',', start_index)
        if end_index == -1:  # Si no encuentra una coma, busca un paréntesis de cierre
            end_index = formula.find(')', start_index)
        # Extrae la referencia de la celda
        cell_ref = formula[start_index:end_index].strip("\"")
        return cell_ref

    def evaluate_formula(self, cells, formula, row, col, access_type, excel_data=None):

        self.excel_data = excel_data
        date_str = None  # Inicialización de date_str 

        # Si la fórmula es TEXTO para obtener el día de la semana
        if formula.startswith("=TEXT"):
            print("Se va a hacer una formula")


            if access_type == "withexceldata":
                print("Se va a hacer una formula con withexceldata")
                # Uso de la función
                cell_ref = self.extract_cell_reference(formula)
                print(f"Referencia de celda extraída: {cell_ref}")
                # Debes asegurarte de asignar un valor a date_str aquí si es necesario
                date_str = self.get_cell_value(cells, cell_ref, access_type) 
                print(f"date_str: {date_str}")
                
                if not isinstance(date_str, datetime.datetime):
                    try:
                        # Asumiendo que date_str es una cadena que representa una fecha, intenta convertirla.
                        date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                    except ValueError as e:
                        # Manejo de error si la cadena no se puede convertir a datetime.
                        print(f"Error al convertir date_str a datetime: {e}")
                        return "Error de conversión"
                else:
                    # Si date_str ya es un objeto datetime, úsalo directamente.
                    date_obj = date_str
                
                
                print(f"date_objet: {date_obj}")
                            
                            # Obtener el día de la semana en inglés
                day_name_english = date_obj.strftime('%A')

                print(f"day_name_english:{day_name_english}")
                            
                            # Traducir el día de la semana al español
                day_name_spanish = self.day_names_spanish.get(day_name_english, "Día desconocido")
                            
                print(f"day_name_spanish{day_name_spanish}")
                return day_name_spanish
                    
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