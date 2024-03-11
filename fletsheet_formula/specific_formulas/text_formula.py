import datetime


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



def text_formula(cell_value, format_str):
    # Asegurarse de que cell_value sea un objeto datetime
    if not isinstance(cell_value, datetime.datetime):
        try:
            # Intenta convertir usando el formato esperado de cell_value
            date_obj = datetime.datetime.strptime(cell_value, "%Y-%m-%d %H:%M:%S")
        except ValueError as e:
            print(f"Error al convertir cell_value a datetime: {e}")
            return "Error de conversión"
    else:
        date_obj = cell_value

    # La lógica para determinar el resultado basado en format_str
    if format_str in ["dddd", "yy", "mmmm"]:
        if format_str == "dddd":
            day_name_english = date_obj.strftime('%A')
            return day_names_spanish.get(day_name_english, "Día no reconocido")
        elif format_str == "yy":
            return date_obj.strftime('%y')
        elif format_str == "mmmm":
            month_name_english = date_obj.strftime('%B')
            return month_names_spanish.get(month_name_english, "Mes no reconocido")
    else:
        return "Formato no reconocido"
