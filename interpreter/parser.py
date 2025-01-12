from interpreter.internals import TokenType
from interpreter.constants import *
from interpreter.grammar import (
    Binary,
    Unary,
    Literal,
    Grouping,
    Variable,
    Logical,
    ReturnStatement,
    Assignment,
    PrintStatement,
    ExpressionStatement,
    VarDeclarationStatement,
    BlockStatement,
    IfStatement,
    WhileStatement,
    FunctionDeclarationStatement,
    Call,
    ClassDeclarationStatement,
    Get,
    Set,
    This
)
import sys


class Parser:
    """
    expression     → assignment ;
    assignment     → IDENTIFIER "=" assignment | logic_or ;
    logic_or       → logic_and ( "or" logic_and )* ;
    logic_and      → equality ( "and" equality )* ;
    equality       → comparison ( ( "!=" | "==" ) comparison )* ;
    comparison     → term ( ( ">" | ">=" | "<" | "<=" ) term )* ;
    term           → factor ( ( "-" | "+" ) factor )* ;
    factor         → unary ( ( "/" | "*" ) unary )* ;
    unary          → ( "!" | "-" ) unary
                   | primary ;
    primary        → NUMBER | STRING | "true" | "false" | "nil"
                   | "(" expression ")" ;
    """

    def __init__(self, tokens):
        self.tokens = tokens
        self.current = 0

    def parse(self):
        statements: list[ExpressionStatement] = []

        while not self.is_at_end():
            statements.append(self.statement())

        return statements

    def advance(self):
        if not self.is_at_end():
            self.current += 1
        return self.previous()

    def is_at_end(self):
        return self.peek().token_type == TokenType.EOF

    def peek(self):
        return self.tokens[self.current]

    def previous(self):
        return self.tokens[self.current - 1]

    def match(self, *types):
        for token_type in types:
            if self.check(token_type):
                self.advance()
                return True
        return False

    def check(self, token_type):
        if self.is_at_end():
            return False
        return self.peek().token_type == token_type

    def consume(self, token_type, message):
        if self.check(token_type):
            return self.advance()
        try:
            raise Exception(message)
        except Exception as e:
            print(e, file=sys.stderr)
            exit(65)

    def expression(self):
        return self.assignment()

    def assignment(self):
        expr = self.logic_or()
        token = self.previous()

        if self.match(TokenType.EQUAL):
            right = self.assignment()

            if isinstance(expr, Variable):
                return Assignment(token, right)
            elif isinstance(expr, Get):
                return Set(expr.object, expr.name, right)

            raise Exception(
                f"on line [{token.line_number}] - Invalid assignment target"
            )

        return expr

    def logic_or(self):
        expression = self.logic_and()

        while self.match(TokenType.OR):
            token = self.previous()
            right = self.logic_and()
            expression = Logical(expression, token, right)

        return expression

    def logic_and(self):
        expression = self.equality()

        while self.match(TokenType.AND):
            token = self.previous()
            right = self.equality()
            expression = Logical(expression, token, right)

        return expression

    def equality(self):
        expr = self.comparison()

        while self.match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
            operator = self.previous()
            right = self.comparison()
            expr = Binary(expr, operator, right)

        return expr

    def comparison(self):
        expr = self.term()

        while self.match(
            TokenType.GREATER,
            TokenType.GREATER_EQUAL,
            TokenType.LESS,
            TokenType.LESS_EQUAL,
        ):
            operator = self.previous()
            right = self.term()
            expr = Binary(expr, operator, right)

        return expr

    def term(self):
        expr = self.factor()

        while self.match(TokenType.MINUS, TokenType.PLUS):
            operator = self.previous()
            right = self.factor()
            expr = Binary(expr, operator, right)

        return expr

    def factor(self):
        expr = self.unary()

        while self.match(TokenType.SLASH, TokenType.STAR):
            operator = self.previous()
            right = self.unary()
            expr = Binary(expr, operator, right)

        return expr

    def unary(self):
        if self.match(TokenType.BANG, TokenType.MINUS):
            operator = self.previous()
            right = self.unary()
            return Unary(operator, right)

        return self.call()

    def call(self):
        expression = self.primary()

        while True:
            if self.match(TokenType.LEFT_PAREN):
                expression = self.finish_call(callee=expression)
            if self.match(TokenType.DOT):
                name = self.consume(TokenType.IDENTIFIER, "Expect property name after '.'.")
                expression = Get(expression, name)
            else:
                break

        return expression

    def finish_call(self, callee):
        arguments = []

        while not self.match(TokenType.RIGHT_PAREN):
            arguments.append(self.expression())
            if len(arguments) >= 255:
                self.consume(self.peek(), "Cannot have more than 255 arguments.")

            if not self.match(TokenType.COMMA):
                break

        if not arguments:
            token = self.previous()
        else:
            token = self.consume(TokenType.RIGHT_PAREN, "Expected ')' after arguments.")

        return Call(callee=callee, arguments=arguments, right_paren=token)

    def primary(self):
        if self.match(
            TokenType.NUMBER,
            TokenType.STRING,
            TokenType.TRUE,
            TokenType.FALSE,
            TokenType.NIL,
        ):
            return Literal(self.previous().literal)

        if self.match(TokenType.IDENTIFIER):
            return Variable(self.previous())

        if self.match(TokenType.THIS):
            return This(self.previous())

        if self.match(TokenType.LEFT_PAREN):
            expression = self.expression()
            line_no = self.peek().line_number
            self.consume(
                TokenType.RIGHT_PAREN,
                f"[line {line_no}] Error at ')': Expect expression",
            )
            return Grouping(expression)

    ################################################################################################

    def statement(self):
        if self.match(TokenType.PRINT):
            return self.print_statement()
        elif self.match(TokenType.VAR):
            return self.variable_declaration_statement()
        elif self.match(TokenType.LEFT_BRACE):
            return self.block_statement()
        elif self.match(TokenType.IF):
            return self.if_statement()
        elif self.match(TokenType.WHILE):
            return self.while_statement()
        elif self.match(TokenType.FOR):
            return self.for_statement()
        elif self.match(TokenType.FUNCTION):
            return self.function_declaration_statement()
        elif self.match(TokenType.RETURN):
            return self.return_statement()
        elif self.match(TokenType.CLASS):
            return self.class_declaration()

        return self.expression_statement()

    def print_statement(self):
        expression = self.expression()
        self.consume(TokenType.SEMICOLON, f"Expected ; after expression.1")
        return PrintStatement(expression)

    def expression_statement(self):
        expression = self.expression()
        self.consume(TokenType.SEMICOLON, f"Expected ; after expression.2")
        return ExpressionStatement(expression)

    def variable_declaration_statement(self):
        token = self.consume(TokenType.IDENTIFIER, "Expect variable name.")

        if self.match(TokenType.EQUAL):
            expression = self.expression()
        else:
            expression = Literal(None)

        self.consume(TokenType.SEMICOLON, f"Expected ; after expression.3")

        return VarDeclarationStatement(token, expression)

    def block_statement(self):
        statements = []

        while not self.check(TokenType.RIGHT_BRACE):
            statement = self.statement()
            statements.append(statement)

        self.consume(TokenType.RIGHT_BRACE, "Expected } after block.")

        return BlockStatement(statements)

    def if_statement(self):
        self.consume(TokenType.LEFT_PAREN, "Expected ( after if.")
        condition = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expected ) after if.")

        if_statement = self.statement()

        if self.match(TokenType.ELSE):
            else_statement = self.statement()
        else:
            else_statement = None

        return IfStatement(condition, if_statement, else_statement)

    def while_statement(self):
        self.consume(TokenType.LEFT_PAREN, "Expected ( after while.")
        condition = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expected ) after while.")

        body = self.statement()

        return WhileStatement(condition, body)

    def for_statement(self):
        self.consume(TokenType.LEFT_PAREN, "Expected ( after for.")
        initializer, condition, increment = None, None, None

        if self.match(TokenType.SEMICOLON):
            initializer = None
        elif self.match(TokenType.VAR):
            initializer = self.variable_declaration_statement()
        else:
            initializer = self.expression_statement()

        if not self.check(TokenType.SEMICOLON):
            condition_statement = self.expression_statement()
        else:
            condition_statement = ExpressionStatement(expression=Literal(True))

        if not self.check(TokenType.RIGHT_PAREN):
            increment = self.expression()

        self.consume(TokenType.RIGHT_PAREN, "Expected ) after for.")

        body = self.statement()

        if increment:
            body = BlockStatement(statements=[body, increment])

        body = WhileStatement(condition=condition_statement.expression, statement=body)

        if initializer:
            body = BlockStatement(statements=[initializer, body])

        return body

    def function_declaration_statement(self):
        name_token = self.consume(TokenType.IDENTIFIER, "Expect function name.")
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after function name.")

        parameters = []

        if not self.check(TokenType.RIGHT_PAREN):
            while True:
                if len(parameters) >= 255:
                    self.consume(self.peek(), "Cannot have more than 255 parameters.")

                parameters.append(
                    self.consume(TokenType.IDENTIFIER, "Expect parameter name.")
                )

                if not self.match(TokenType.COMMA):
                    break

        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after parameters.")
        self.consume(TokenType.LEFT_BRACE, "Expect '{' before function body.")

        body = self.block_statement()
        return FunctionDeclarationStatement(name_token, parameters, body)

    def return_statement(self):
        keyword = self.previous()
        expression = None

        if not self.check(TokenType.SEMICOLON):
            expression = self.expression()

        self.consume(TokenType.SEMICOLON, "Expected ; after return value.")
        return ReturnStatement(keyword, expression)

    def class_declaration(self):
        name_token = self.consume(TokenType.IDENTIFIER, "Expect class name.")
        super_class = None


        if self.match(TokenType.EXTENDS):
            super_class = self.consume(TokenType.IDENTIFIER, "Expect superclass name.")
            super_class = Variable(super_class)

        self.consume(TokenType.LEFT_BRACE, "Expect '{' before class body.")

        methods = []

        while not self.check(TokenType.RIGHT_BRACE):
            methods.append(self.function_declaration_statement())

        self.consume(TokenType.RIGHT_BRACE, "Expect '}' after class body.")

        return ClassDeclarationStatement(name_token, methods, super_class)
