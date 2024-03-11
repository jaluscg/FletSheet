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
            print(f"col:{col}")
            print(f"row:{row}")
            print(f"value:{value}")
                
            return value

    def extract_cell_reference_and_format(self, formula):
        # Eliminar espacios extra y comillas al inicio y final, si existen
        formula = formula.strip().strip('"')
        
        # Encuentra el inicio y fin de la parte interna de la fórmula
        start_index = formula.find('(') + 1
        end_index = formula.find(')', start_index)
        if start_index == 0 or end_index == -1:
            print("Formato de fórmula incorrecto. Asegúrate de que la fórmula tenga el formato correcto.")
            return [], []  # Cambio aquí: retorna listas vacías en lugar de None
        
        # Extraer la parte interna de la fórmula
        formula_part = formula[start_index:end_index]
        print(f"formula_part{formula_part}")
        
        # Buscar referencias de celdas, rangos y posiblemente formatos o constantes
        pattern = r'([A-Z]+[0-9]+:[A-Z]+[0-9]+|[A-Z]+[0-9]+|"[^"]*"|\d+\.?\d*)'
        matches = re.findall(pattern, formula_part)
        print(f"matches:{matches}")
        
        # Separar referencias de celdas, rangos y otros elementos
        cell_references = []
        formats = []
        for match in matches:
            if ':' in match or re.match(r'[A-Z]+[0-9]+$', match):
                cell_references.append(match)
                print(f"cell_references:{cell_references}")
            else:
                formats.append(match.strip('"'))
                print(f"formats:{formats}")

        
        # Devuelve una lista de referencias de celdas y otra lista con formatos u otros elementos
        return cell_references, formats


    def evaluate_subformula(self, cells, subformula, row, col, access_type):
        return self.evaluate_formula(cells, subformula, row, col, access_type)

    def evaluate_formula(self, cells, formula, row, col, access_type, excel_data=None):

        self.excel_data = excel_data

        """
        if '&' in formula:
            subformulas = formula.split('&')
            results = []
            for sub in subformulas:
                sub = sub.strip()
                if sub.startswith("=TEXT") or sub.startswith("TEXT("):
                    cell_ref, format_str = self.extract_cell_reference_and_format(sub)
                    if cell_ref:
                        cell_value = self.get_cell_value(cells, cell_ref, access_type)
                        formatted_value = text_formula(cell_value, format_str, access_type,
                                                        get_cell_value_func=self.get_cell_value, cells=cells)
                        results.append(formatted_value)
                    else:
                        print("Subfórmula TEXT con formato incorrecto")
                        results.append("")  # O manejar el error de manera apropiada
                else:
                    # Manejar otras subfórmulas si es necesario
                    pass

            
            return ''.join(results)
           
        
        else:  """
     
        if formula.startswith("=TEXT"):
            cell_references, formats = self.extract_cell_reference_and_format(formula) if access_type == "withexceldata" else ([], None)
            if access_type != "withexceldata":
                match = re.match(r'=TEXT\((?P<cell_ref>[A-Z]+\d+); ?"(?P<format_str>dddd|yy|mmmm)"\)', formula)
                if match:
                    cell_references = [match.group('cell_ref')]  # Convirtiendo el valor en una lista
                    formats =  [match.group('format_str')]  
            if cell_references:
                for cell_ref in cell_references:
                    date_str = self.get_cell_value(cells, cell_ref, access_type) if access_type == "withexceldata" else formula
                    print(f"date_str:{date_str}")
                    # Asegúrate de pasar una cadena como format_str, usando formats[0] si formats no está vacío
                    result = text_formula(date_str, formats[0] if formats else "Formato desconocido")
                    print(f"result:{result}")
                    return result
            else:
                print("Error: Referencia de celda o formato no válido.")

                

                    
            
                
        else:
            if access_type == "withexceldata":
                # Verificar si la fórmula contiene funciones complejas o rangos, los cuales no queremos evaluar.
                # Este regex busca funciones comunes de Excel y el uso de ':' para rangos.
                print(f"formula:{formula}")
                if re.search(r'(\w+\()|:', formula):
                    print("La fórmula contiene funciones complejas o rangos que no se evaluarán.")
                    # Puedes decidir qué hacer en este caso, por ejemplo, retornar un valor por defecto o el mismo texto de la fórmula.
                    cells[row][col] = "Fórmula no soportada"
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
                    cells[row][col].content.value = result
                elif access_type == "withdictionary":
                    cells[row][col] = result
                elif access_type == "withexceldata":
                    # Aquí se decide qué hacer con el resultado, por ejemplo, podrías querer actualizar cells directamente si es necesario.
                    cells[row][col] = result
                return result
            except Exception as e:
                print(f"Error evaluando la fórmula: {e}")
                # Manejar el error de manera apropiada, por ejemplo, asignando un valor de error a la celda.
                cells[row][col] = "Error en fórmula"
                return "Error en fórmula"
            
            """
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

                  """