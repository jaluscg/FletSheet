class Funciones:
    
    @staticmethod
    def get_cell_value(cells, cell_ref):
        col = ord(cell_ref[0]) - 65  # Convertir A, B, C, ... a 0, 1, 2, ...
        row = int(cell_ref[1:]) - 1
        return float(cells[row][col].value)
    
    @staticmethod
    def SUM(cells, *args):
        result = 0
        for cell_ref in args:
            result += Funciones.get_cell_value(cells, cell_ref)
        return result
    
    @staticmethod
    def ADD(cells, *args):
        result = 0
        for arg in args:
            if re.match(r"^[A-Z]\d$", arg):  # Si el argumento es una referencia de celda
                result += Funciones.get_cell_value(cells, arg)
            else:  # Si el argumento es un número
                result += float(arg)
        return result
