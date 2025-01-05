from interpreter.grammar import Expression, Binary, Unary, Literal, Grouping, Variable
import sys

class AstPrinter:
    # TODO: implement visitor pattern or move it to grammer's toString methods
    def print(self, expression: Expression) -> str:
        return self.parenthesize("", expression).strip()

    def visit_binary(self, binary: Binary) -> str:
        return self.parenthesize(binary.operator.lexeme, binary.left, binary.right)

    def visit_unary(self, unary: Unary) -> str:
        return self.parenthesize(unary.operator.lexeme, unary.right)

    def visit_literal(self, literal: Literal) -> str:
        return str(literal.value)

    def visit_grouping(self, grouping: Grouping) -> str:
        return self.parenthesize("group", grouping.expression)

    def parenthesize(self, name: str, *expressions: Expression) -> str:
        result = f"({name}" if name else ""

        for exp in expressions:
            if isinstance(exp, Binary):
                result += " " + self.visit_binary(exp)
            elif isinstance(exp, Unary):
                result += " " + self.visit_unary(exp)
            elif isinstance(exp, Literal):
                result += " " + self.visit_literal(exp)
            elif isinstance(exp, Grouping):
                result += " " + self.visit_grouping(exp)
            else:
                print("exp", exp.__str__)

        return result + ")" if name else result


def main():
    from interpreter.internals import Token

    minus = Token("MINUS", "-", 1, 1)

    expression = Binary(
        Unary(minus, Literal(3)),
        Token("STAR", "*", 1, 1),
        Grouping(Literal(45.234)),
    )

    printer = AstPrinter()
    print(printer.print(expression))


if __name__ == "__main__":
    main()
