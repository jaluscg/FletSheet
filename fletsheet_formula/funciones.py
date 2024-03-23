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
        self.formula_results = {}
        
        

      

    def get_cell_value(self, cell_ref, access_type, excel_data=None, current_sheet_name=None, cells=None):
            

            # Decide entre 'withexceldata' y otros modos aquí directamente
            if access_type == "withexceldata" and excel_data is not None:
                        return self.get_cell_value_with_excel_data(cell_ref, excel_data, current_sheet_name)
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
    
    def column_to_index(self, column_name):
        """Convierte un nombre de columna Excel (e.g., 'A', 'Z', 'AA') a un índice numérico (0-based)."""
        column_name = column_name.upper()
        index = 0
        for char in column_name:
            index = index * 26 + (ord(char) - ord('A') + 1)
        print(f"Converting column {column_name} to index {index - 1}")
        return index - 1

    def evaluate_range(self, range_ref, excel_data, current_sheet_name):
        # Extrae el nombre de la hoja y el rango de la referencia
        if '!' in range_ref:
            sheet_name, cell_range = range_ref.split('!')
        else:
            sheet_name = current_sheet_name
            cell_range = range_ref
        sheet_data = excel_data.get(sheet_name, [])

        # Procesa rangos de celdas completos (ej. 'A:A', '1:1')
        if ':' in cell_range:
            start_ref, end_ref = cell_range.split(':')
            if start_ref.isalpha() and end_ref.isalpha():  # Columna completa (ej. 'A:A')
                col_index = self.column_to_index(start_ref)
                return [row[col_index] for row in sheet_data]
            elif start_ref.isdigit() and end_ref.isdigit():  # Fila completa (ej. '1:1')
                row_index = int(start_ref) - 1
                return sheet_data[row_index] if 0 <= row_index < len(sheet_data) else []
            else:  # Rango específico (ej. 'A1:B2')
                # Implementa lógica para procesar un rango específico de celdas
                pass  # Este es un ejemplo, necesitas implementar esta parte
        else:  # Referencia a una única celda (ej. 'A1')
            col_name = ''.join(filter(str.isalpha, cell_range))
            row_index = int(''.join(filter(str.isdigit, cell_range))) - 1
            col_index = self.column_to_index(col_name)
            return sheet_data[row_index][col_index] if 0 <= row_index < len(sheet_data) else None

        
    def get_cell_value_with_excel_data(self, cell_ref, excel_data, current_sheet_name):
        # Debug: Imprime la referencia de celda procesada
        print(f"Procesando referencia de celda: {cell_ref}")

        # Divide la referencia de la celda en componentes usando la expresión regular mejorada
        components = re.findall(r"('[^']+'!)?([A-Z]+:[A-Z]+|[0-9]+:[0-9]+|[A-Z]+\d+(:[A-Z]+\d+)?)(\"[^\"]+\")?", cell_ref)

        results = []
        for component in components:
            # Extrae solo las partes relevantes de cada componente
            sheet_ref, cell_range, _1, format_str = component
            full_ref = f"{sheet_ref}{cell_range}"
            # Debug: Imprime la referencia completa de celda procesada
            print(f"Procesando componente: {full_ref}, formato: {format_str}")
            
            result = self.evaluate_range(full_ref, excel_data, current_sheet_name)
            results.append(result)

        # Combina los resultados según sea necesario
        # Este es un ejemplo; ajusta según tus necesidades
        combined_result = sum(results) if isinstance(results[0], (list, int, float)) else results
        print(f"Resultado combinado: {combined_result}")
        return combined_result
        
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


    def evaluate_formula(self,formula, access_type, excel_data=None, current_sheet_name=None, cells=None):

        # Este bloque es universal para todas las fórmulas.
        cell_references, formats = self.extract_cell_reference_and_format(formula)

        
            
        # Manejar fórmulas TEXT
        if formula.startswith(("=TEXT", "TEXT(")):
            results = []
            for index, cell_ref in enumerate(cell_references):
                # Asegúrate de manejar correctamente valores únicos y listas
                raw_value = self.get_cell_value(cell_ref, access_type, excel_data, current_sheet_name, cells)
                # Si el valor es una lista y se espera un solo valor, toma el primer elemento
                if isinstance(raw_value, list) and len(raw_value) > 0:
                    date_str = raw_value[0]
                else:
                    date_str = raw_value
                print(f"Valor de celda para TEXT: {date_str}")

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
                    return sumifs_formula(sum_range, criteria_range, criteria, access_type,excel_data, current_sheet_name, cells,)
                else:
                    print("Fórmula SUMIFS con número incorrecto de argumentos.")
                    return "Fórmula SUMIFS con número incorrecto de argumentos."            
            
        elif formula.startswith(("=SUM", "SUM(")):
                print(f"len(cell_references):{len(cell_references)}")
                range_sum = 0
                for cell_ref in cell_references:
                    range_sum += sum_formula(cells, cell_ref, access_type, excel_data, current_sheet_name)
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
                