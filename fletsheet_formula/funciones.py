import re
import datetime
from .specific_formulas.text_formula import text_formula

class Formulas():
    """
    Conjunto de formulas para evaluar en la matriz de celdas
    """

    def __init__(self):
        self.excel_data = None

      

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

    def extract_cell_reference_and_format(self, formula):
        # Encuentra el inicio de la referencia de la celda y el formato
        start_index = formula.find('(') + 1
        end_index = formula.find(')', start_index)
        formula_part = formula[start_index:end_index]

        # Intenta dividir la parte de la fórmula en referencia de celda y formato usando tanto coma como punto y coma
        for delimiter in [',', ';']:
            if delimiter in formula_part:
                parts = formula_part.split(delimiter)
                cell_ref = parts[0].strip().strip("\"")
                format_str = parts[1].strip().strip("\"") if len(parts) > 1 else ""
                return cell_ref, format_str

        # Si no se encuentra ni coma ni punto y coma, asume que el formato de la fórmula es incorrecto
        print("Formato de fórmula incorrecto. Asegúrate de que la fórmula tenga el formato correcto, como =TEXT(A2;\"dddd\")")
        return None, None

    def evaluate_formula(self, cells, formula, row, col, access_type, excel_data=None):

        self.excel_data = excel_data
        
        if formula.startswith("=TEXT"):
            cell_ref, format_str = self.extract_cell_reference_and_format(formula) if access_type == "withexceldata" else (None, None)
            if access_type != "withexceldata":
                # Para los casos sin withexceldata, necesitamos capturar la referencia de la celda y el formato directamente del match
                match = re.match(r'=TEXT\((?P<cell_ref>[A-Z]+\d+); ?"(?P<format_str>dddd|yy|mmmm)"\)', formula)
                if match:
                    cell_ref = match.group('cell_ref')
                    format_str = match.group('format_str')
            
            if cell_ref is not None:
                date_str = self.get_cell_value(cells, cell_ref, access_type) if access_type == "withexceldata" else formula
                # Pasamos el access_type a text_formula
                result = text_formula(date_str, format_str, access_type, get_cell_value_func=self.get_cell_value, cells=cells )
                return result
            else:
                print("Error: Referencia de celda o formato no válido.")
                

        
                
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