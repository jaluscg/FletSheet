import re
import datetime
from .specific_formulas.text_formula import text_formula
from .specific_formulas.sum_formula import sum_formula

class Formulas():
    """
    Conjunto de formulas para evaluar en la matriz de celdas
    """

    def __init__(self):
        self.excel_data = None

      

    def get_cell_value(self, cells, cell_ref, access_type):
            

            # Decide entre 'withexceldata' y otros modos aquí directamente
            if access_type == "withexceldata" and self.excel_data is not None:
                return self.get_cell_value_from_excel_formulas(cell_ref)
            else:
                # Lógica para 'withcell' y 'withdictionary'
                if access_type == "withcell":
                    col = ord(cell_ref[0]) - 65
                    row = int(cell_ref[1:]) - 1
                    # Acceso directo a la celda, retorna el valor tal como está
                    return cells[row][col].content.value
                elif access_type == "withdictionary":
                    # Acceso a través del diccionario, retorna el valor tal como está
                    col = ord(cell_ref[0]) - 65
                    row = int(cell_ref[1:]) - 1
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
            #print(f"col:{col}")
            #print(f"row:{row}")
            #print(f"value:{value}")
                
            return value

    def extract_cell_reference_and_format(self, formula):
        print(f"Formula original: {formula}")
        formula = formula.strip().strip('"')

        start_index = formula.find('(') + 1
        end_index = formula.rfind(')')
        print(f"Índices de inicio y fin de la parte interna de la fórmula: {start_index}, {end_index}")

        if start_index == 0 or end_index == -1:
            print("Formato de fórmula incorrecto.")
            return [], []

        formula_part = formula[start_index:end_index]
        print(f"Parte interna de la fórmula: {formula_part}")

        pattern = r'([A-Z]+[0-9]+(?::[A-Z]+[0-9]+)?|"[^"]*"|\&|\d+\.?\d*)'
        matches = re.findall(pattern, formula_part)
        print(f"Componentes encontrados con regex: {matches}")

        cell_references = []
        formats = []
        for match in matches:
            if ':' in match or re.match(r'[A-Z]+[0-9]+$', match):
                cell_references.append(match)
                print(f"Referencia de celda añadida: {match}")
            elif match != '&':  # Excluyendo explícitamente el operador de concatenación
                formats.append(match.strip('"'))
                

        return cell_references, formats


    def evaluate_formula(self, cells, formula, row, col, access_type, excel_data=None):

        self.excel_data = excel_data
        # Este bloque es universal para todas las fórmulas.
        cell_references, formats = self.extract_cell_reference_and_format(formula)

        
            
        
            # Ahora maneja la fórmula basándose en el tipo detectado.
        if formula.startswith(("=TEXT", "TEXT(")):
                results = []
                for cell_ref in cell_references:
                    date_str = self.get_cell_value(cells, cell_ref, access_type)
                    result = text_formula(date_str, formats[0] if formats else "Formato desconocido")
                    results.append(result)
                return ''.join(results)
            
        elif formula.startswith(("=SUM", "SUM(")):
                range_sum = 0
                for cell_ref in cell_references:
                    range_sum += sum_formula(cells, cell_ref)
                return range_sum
               
                
                    
        else:
                if access_type == "withexceldata":
                    # Verificar si la fórmula contiene funciones complejas o rangos, los cuales no queremos evaluar.
                    # Este regex busca funciones comunes de Excel y el uso de ':' para rangos.
                    print(f"formula:{formula}")
                    if re.search(r'(\w+\()|:', formula):
                        print("La fórmula contiene funciones complejas o rangos que no se evaluarán.")
                        # Puedes decidir qué hacer en este caso, por ejemplo, retornar un valor por defecto o el mismo texto de la fórmula.
                        return "Fórmula no soportada"
                    else:
                        cell_references, _ = self.extract_cell_reference_and_format(formula)
                        for cell_ref in cell_references:
                            cell_value = self.get_cell_value_from_excel_formulas(cell_ref)
                            cell_value_str = repr(cell_value)
                            formula = formula.replace(cell_ref, cell_value_str)

                try:
                    # Procesar la fórmula sencilla utilizando eval para el cálculo final
                    formula_eval = re.sub(r'([A-Z]+)(\d+)', lambda match: str(self.get_cell_value(cells, match.group(0), access_type)), formula.lstrip('='))
                    result = eval(formula_eval)
                    if access_type == "withcell":
                        return result
                    elif access_type == "withdictionary":
                        return result
                    elif access_type == "withexceldata":
                        return result 

                except Exception as e:
                    print(f"Error evaluando la fórmula: {e}")
                    # Manejar el error de manera apropiada, por ejemplo, asignando un valor de error a la celda.
                    return "Error en fórmula"
                