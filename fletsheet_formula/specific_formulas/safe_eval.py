import ast
import operator

# Función para evaluar de forma segura expresiones matemáticas como strings
def safe_eval(expr):
    # Define los operadores permitidos
    operators = {
        ast.Add: operator.add, ast.Sub: operator.sub,
        ast.Mult: operator.mul, ast.Div: operator.truediv,
        ast.Pow: operator.pow, ast.BitXor: operator.xor,
        ast.USub: operator.neg,
    }

    class Evaluator(ast.NodeVisitor):
        def visit_BinOp(self, node):
            left = self.visit(node.left)
            right = self.visit(node.right)
            return operators[type(node.op)](left, right)

        def visit_Num(self, node):
            return node.n

        def visit_UnaryOp(self, node):
            operand = self.visit(node.operand)
            return operators[type(node.op)](operand)

    tree = ast.parse(expr, mode='eval')
    evaluator = Evaluator()
    return evaluator.visit(tree.body)