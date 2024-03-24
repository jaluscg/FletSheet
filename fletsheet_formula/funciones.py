import re
import datetime
from .specific_formulas.text_formula import text_formula
from .specific_formulas.sum_formula import sum_formula
from .specific_formulas.sumifs_formula import sumifs_formula
from .specific_formulas.safe_eval import safe_eval

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

    def remove_quotes(self,sheet_name):
        """Quita las comillas simples del inicio y final del nombre de la hoja, si existen."""
        if sheet_name.startswith("'") and sheet_name.endswith("'"):
            return sheet_name[1:-1]
        return sheet_name


    def evaluate_range(self, range_ref, excel_data, current_sheet_name):
        print(f"Debug: evaluate_range called with range_ref={range_ref}, current_sheet_name={current_sheet_name}")
        if '!' in range_ref:
            sheet_name, cell_range = range_ref.split('!')
            # Quita las comillas del nombre de la hoja usando la función remove_quotes.
            sheet_name = self.remove_quotes(sheet_name)
        else:
            sheet_name = current_sheet_name
            cell_range = range_ref
        sheet_data = excel_data.get(sheet_name, [])
        print(f"Debug: Sheet '{sheet_name}' data loaded, total rows: {len(sheet_data)}")

        if ':' in cell_range:
            start_ref, end_ref = cell_range.split(':')
            print(f"Debug: Procesando rango de celdas: {start_ref} a {end_ref}")
            if start_ref.isalpha() and end_ref.isalpha():  # Columna completa (ej. 'A:A')
                col_index_start = self.column_to_index(start_ref)
                col_index_end = self.column_to_index(end_ref)
                range_values = [row[col_index_start:col_index_end + 1] for row in sheet_data]
                print(f"Debug: Valores en rango de columnas: {range_values}")
            elif start_ref.isdigit() and end_ref.isdigit():  # Fila completa (ej. '1:1')
                row_index_start = int(start_ref) - 1
                row_index_end = int(end_ref) - 1
                range_values = sheet_data[row_index_start:row_index_end + 1]
                print(f"Debug: Valores en rango de filas: {range_values}")
            else:  # Rango específico (ej. 'A1:B2')
                start_col_name = ''.join(filter(str.isalpha, start_ref))
                start_row_index = int(''.join(filter(str.isdigit, start_ref))) - 1
                end_col_name = ''.join(filter(str.isalpha, end_ref))
                end_row_index = int(''.join(filter(str.isdigit, end_ref))) - 1

                start_col_index = self.column_to_index(start_col_name)
                end_col_index = self.column_to_index(end_col_name)

                print(f"Debug: Procesando rango de celdas específico desde {start_col_name}{start_row_index+1} hasta {end_col_name}{end_row_index+1}")
                range_values = []
                for row_index, row in enumerate(sheet_data[start_row_index:end_row_index + 1], start=start_row_index):
                    cell_values = row[start_col_index:end_col_index + 1]
                    print(f"Debug: Valores en fila {row_index + 1}: {cell_values}")
                    range_values.extend(cell_values)
        else:
            # Manejo de una única celda (ej. 'A1')
            col_name = ''.join(filter(str.isalpha, cell_range))
            row_index = int(''.join(filter(str.isdigit, cell_range))) - 1
            col_index = self.column_to_index(col_name)
            cell_value = sheet_data[row_index][col_index] if 0 <= row_index < len(sheet_data) else None
            range_values = [cell_value]
            print(f"Debug: Valor de la celda {cell_range}: {cell_value}")

        return range_values

        
    def get_cell_value_with_excel_data(self, cell_ref, excel_data, current_sheet_name):
        print(f"Procesando referencia de celda: {cell_ref}")

        components = re.findall(r"('[^']+'!)?([A-Z]+:[A-Z]+|[0-9]+:[0-9]+|[A-Z]+\d+(:[A-Z]+\d+)?)(\"[^\"]+\")?", cell_ref)
        print(f"Componentes encontrados con regex: {components}")

        results = []
        for component in components:
            sheet_ref, cell_range, _1, format_str = component
            full_ref = f"{sheet_ref}{cell_range}"
            print(f"Debug: Iniciando procesamiento de componente {full_ref}, tipo: {'Rango' if ':' in cell_range else 'Celda'}")


            result = self.evaluate_range(full_ref, excel_data, current_sheet_name)
            if result is not None:
                if isinstance(result, list):
                    evaluated_results = []
                    for item in result:
                        if isinstance(item, str) and item.startswith('='):
                            evaluated_result = self.evaluate_formula(item, "withexceldata", excel_data, current_sheet_name)
                            evaluated_results.append(evaluated_result)
                        else:
                            evaluated_results.append(item)
                    results.extend(evaluated_results)
                else:
                    if isinstance(result, str) and result.startswith('='):
                        result = self.evaluate_formula(result, "withexceldata", excel_data, current_sheet_name)  # Corregido aquí
                    results.append(result)

        print(f"Debug: Resultado combinado: {results}")
        return results


    def extract_cell_reference_and_format(self, formula):
        print(f"Formula original: {formula}")
        formula = formula.strip().strip('"')

        # Verificar si la fórmula contiene paréntesis (indicando una función)
        if '(' in formula and ')' in formula:
            start_index = formula.find('(') + 1
            end_index = formula.rfind(')')
            print(f"Índices de inicio y fin de la parte interna de la fórmula: {start_index}, {end_index}")

            if start_index == 0 or end_index == -1:
                print("Formato de fórmula incorrecto.")
                return [], []

            formula_part = formula[start_index:end_index]
        else:
            # Para expresiones simples, toda la fórmula es considerada como la "parte interna"
            formula_part = formula
            start_index, end_index = 0, len(formula)  # Ajustar índices para reflejar toda la longitud de la fórmula
            print(f"Expresión simple o fórmula sin función: {formula_part}")

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
                print("se hará formula sumifs")
                sum_range = self.get_cell_value_with_excel_data(cell_references[0], excel_data, current_sheet_name)
                criteria_range = self.get_cell_value_with_excel_data(cell_references[1], excel_data, current_sheet_name)
                criteria = self.get_cell_value_with_excel_data(cell_references[2], excel_data, current_sheet_name)[0]
                print(f"sum_range:{sum_range}")
                print(f"criteria_range:{criteria_range}")
                print(f"criteria:{criteria}")

                total_sum = 0

                if len(sum_range) != len(criteria_range):
                    print("Los rangos de suma y criterios no coinciden en longitud.")
                    return 0

                for i in range(len(criteria_range)):
                    criteria_value = criteria_range[i][0]

                    if criteria_value == criteria:
                        sum_value = sum_range[i][0]
                        # Verifica si sum_value es una fórmula
                        if isinstance(sum_value, str) and sum_value.startswith('='):
                            # Evalúa la fórmula
                            evaluated_value = self.evaluate_formula(sum_value, access_type, excel_data, current_sheet_name, cells)
                            # Asegura que el valor evaluado es numérico antes de sumarlo
                            if isinstance(evaluated_value, (int, float)):
                                total_sum += evaluated_value
                            else:
                                print(f"El valor evaluado no es numérico en sum_range en la posición {i}: {evaluated_value}")
                        elif isinstance(sum_value, (int, float)):
                            total_sum += sum_value
                        else:
                            print(f"Valor no numérico en sum_range en la posición {i}: {sum_value}")

                return total_sum
            else:
                print("Fórmula SUMIFS con número incorrecto de argumentos.")
                return "Fórmula SUMIFS con número incorrecto de argumentos."
         
            
        elif formula.startswith(("=SUM", "SUM(")):
            total_sum = 0.0
            for cell_ref in cell_references:
                # Obtiene el valor o los valores utilizando get_cell_value_with_excel_data
                values = self.get_cell_value_with_excel_data(cell_ref, excel_data, current_sheet_name)
                # Si values es una lista, intenta convertir y sumar todos sus elementos válidos; de lo contrario, suma el valor directamente si es numérico
                if isinstance(values, list):
                    for value in values:
                        try:
                            # Intenta convertir cada valor a un número. Si no es posible, lo ignora.
                            num_value = float(value) if value is not None else 0
                            total_sum += num_value
                        except ValueError:
                            # Aquí manejas valores que no se pueden convertir a flotante, como cadenas de texto.
                            print(f"No se puede sumar el valor no numérico: {value}")
                else:
                    # Para un valor único, verifica y suma si es numérico.
                    try:
                        if values is not None:
                            num_value = float(values)
                            total_sum += num_value
                    except ValueError:
                        print(f"No se puede sumar el valor no numérico: {values}")
            return total_sum
        
        else:
                
                    # Verificar si la fórmula contiene funciones complejas o rangos, los cuales no queremos evaluar.
                    # Este regex busca funciones comunes de Excel y el uso de ':' para rangos.
                    print(f"formula:{formula}")
                    if re.search(r'(\w+\()|:', formula):
                        print("La fórmula contiene funciones complejas o rangos que no se evaluarán.")
                        return "Fórmula no soportada"
                    else:

                        print(f"cell_references:{cell_references}")

                        try:
                            for cell_ref in cell_references:
                                # Obtiene el valor de la celda utilizando tu método existente
                                value = self.get_cell_value_with_excel_data(cell_ref, excel_data, current_sheet_name)
                                # Asegúrate de que value sea una lista con un solo elemento o un valor escalar
                                value = value[0] if isinstance(value, list) and len(value) == 1 else value
                                # Reemplaza la referencia en la fórmula por su valor (como string)
                                formula = formula.replace(cell_ref, str(value), 1)
                            
                            #print(f"Fórmula con valores reemplazados: {formula}")
                            
                            # Evalúa la fórmula reemplazada (que ahora solo contiene números y operadores)
                            print(f"Debug: Evaluando fórmula simplificada: {formula}")
                            result = safe_eval(formula[1:])  # [1:] para quitar el signo '=' al inicio
                            return result            


                        except Exception as e:
                            print(f"Error evaluando la fórmula: {e}")
                            print(f"Debug: error en fórmula simplificada: {formula}")
                            return "Error en fórmula"