import re
import datetime
from .specific_formulas.text_formula import text_formula
from .specific_formulas.sum_formula import sum_formula
from .specific_formulas.sumifs_formula import sumifs_formula

class Formulas():
    """
    Conjunto de formulas para evaluar en la matriz de celdas
    """

    def __init__(self):
        self.excel_data = None
        self.current_sheet_name = None
        

      

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
        # Dividir la referencia de la celda en nombre de la hoja y celda (si es que viene con hoja)
        parts = cell_ref.split('!')
        if len(parts) == 2:
            sheet_name, cell = parts
        else:
            # Si no se proporciona el nombre de la hoja, usa current_sheet_name
            sheet_name = self.current_sheet_name
            cell = cell_ref

        col = ord(cell[0]) - 65
        row = int(cell[1:]) - 1

        # Verificar si el nombre de la hoja existe en excel_data
        if sheet_name in self.excel_data:
            sheet_data = self.excel_data[sheet_name]
            if row < len(sheet_data) and col < len(sheet_data[row]):
                return sheet_data[row][col]
            else:
                print(f"Índices fuera de límites para la hoja '{sheet_name}' con referencia {cell_ref}.")
                return None
        else:
            print(f"Nombre de hoja '{sheet_name}' no encontrado en excel_data.")
            return None
    
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

        # Patrón regex ajustado para capturar rangos completos, referencias de hojas y cadenas entre comillas
        pattern = r"('[^']+'!)?([A-Z]+:[A-Z]+|[A-Z]+\d+(:[A-Z]+\d+)?)|(\"[^\"]+\")"
        matches = re.findall(pattern, formula_part)
        print(f"Componentes encontrados con regex: {matches}")

        cell_references = []
        formats = []
        for match in matches:
            # Combinar el nombre de la hoja (si existe) con la referencia de celda/rango
            ref = (match[0] if match[0] else '') + (match[1] if match[1] else '')
            if ref:
                cell_references.append(ref)
                print(f"Referencia de celda añadida: {ref}")
            elif match[3]:  # Captura de cadenas entre comillas
                formats.append(match[3].strip('"'))

        return cell_references, formats


    def evaluate_formula(self, cells, formula, row, col, access_type, excel_data=None, current_sheet_name=None):

        self.excel_data = excel_data
        self.current_sheet_name = current_sheet_name

        # Este bloque es universal para todas las fórmulas.
        cell_references, formats = self.extract_cell_reference_and_format(formula)

        
            
        # Manejar fórmulas TEXT
        if formula.startswith(("=TEXT", "TEXT(")):
            results = []
            # Asegurarse de aplicar cada formato correspondiente a su celda
            for index, cell_ref in enumerate(cell_references):
                date_str = self.get_cell_value(cells, cell_ref, access_type)
                # Usa el formato correspondiente por índice, o el primer formato si hay más celdas que formatos
                format_str = formats[index] if index < len(formats) else formats[0]
                result = text_formula(date_str, format_str)
                results.append(result)
            return ''.join(results)
        
        elif formula.startswith(("=SUMIFS", "SUMIFS(")):
                print(f"len(cell_references):{len(cell_references)}")
                if len(cell_references) == 3: 
                    sum_range = cell_references[0]
                    criteria_range = cell_references[1]
                    criteria = cell_references[2]
                    print("se hará formula sumifs")
                    
                    # Si las referencias incluyen nombres de hojas, se pasan directamente.
                    # La función sumifs_formula será responsable de interpretar estos correctamente.
                    return sumifs_formula(cells, sum_range, criteria_range, criteria, self.excel_data)
                else:
                    print("Fórmula SUMIFS con número incorrecto de argumentos.")
                    return "Fórmula SUMIFS con número incorrecto de argumentos."            
            
        elif formula.startswith(("=SUM", "SUM(")):
                print(f"len(cell_references):{len(cell_references)}")
                range_sum = 0
                for cell_ref in cell_references:
                    range_sum += sum_formula(cells, cell_ref, access_type, self.excel_data)
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
                