import datetime
import re

month_names_spanish = {
        'January': 'enero',
        'February': 'febrero',
        'March': 'marzo',
        'April': 'abril',
        'May': 'mayo',
        'June': 'junio',
        'July': 'julio',
        'August': 'agosto',
        'September': 'septiembre',
        'October': 'octubre',
        'November': 'noviembre',
        'December': 'diciembre',
    }

day_names_spanish = {
        'Monday': 'lunes',
        'Tuesday': 'martes',
        'Wednesday': 'miércoles',
        'Thursday': 'jueves',
        'Friday': 'viernes',
        'Saturday': 'sábado',
        'Sunday': 'domingo',
    }



def text_formula(cell_value, format_str, access_type):
    if access_type == "withexceldata":
        if not isinstance(cell_value, datetime.datetime):
            try:
                date_obj = datetime.datetime.strptime(cell_value, "%Y-%m-%d %H:%M:%S")
            except ValueError as e:
                print(f"Error al convertir cell_value a datetime: {e}")
                return "Error de conversión"
        else:
            date_obj = cell_value
    else:
        # Manejo del caso cuando access_type no es withexceldata
        match = re.match(r'=TEXT\((?P<cell_ref>[A-Z]+\d+); ?"(?P<format_str>dddd|yy|mmmm)"\)', cell_value)
        if match:
            format_str = match.group("format_str")
            # Aquí asumimos que la conversión de la fecha ya se ha hecho fuera de esta función
            date_obj = cell_value
        else:
            return "Formato no reconocido"

    # La lógica para determinar el resultado basado en format_str
    if format_str == "dddd":
        day_name_english = date_obj.strftime('%A')
        day_name_spanish = day_names_spanish[day_name_english]
        return day_name_spanish
    elif format_str == "yy":
        return date_obj.strftime('%y')
    elif format_str == "mmmm":
        month_name_english = date_obj.strftime('%B')
        month_name_spanish = month_names_spanish[month_name_english]
        return month_name_spanish
    else:
        return "Formato no reconocido"


"""
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
        """