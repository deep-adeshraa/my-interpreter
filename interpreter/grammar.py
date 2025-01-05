from interpreter.constants import *
from interpreter.internals import Token, TokenType
from interpreter.environment import Environment
from contextlib import contextmanager
from interpreter.callable import MyCallable, MyFunction, MyClass, MyInstance
from interpreter.resolver import Resolver

"""
expression     → literal
               | unary
               | binary
               | grouping
               | variable
               | logical
               | call;

literal        → NUMBER | STRING | "true" | "false" | "nil" ;
grouping       → "(" expression ")" ;
unary          → ( "-" | "!" ) expression;
call           → primary ( "(" arguments? ")" )*
get            → primary "." IDENTIFIER ;
binary         → expression operator expression ;
operator       → "==" | "!=" | "<" | "<=" | ">" | ">="
               | "+"  | "-"  | "*" | "/" ;
variable       → IDENTIFIER
logical        → expression operator expression
"""

environment = Environment()
depth_map = {}


def resolve(expression, depth):
    depth_map[expression] = depth


def lookup_variable(token, expression):
    distance = depth_map.get(expression)

    if distance is not None:
        return environment.get_at(distance, token)
    else:
        return environment.get(token)


@contextmanager
def swap_environment(new_environment):
    global environment
    try:
        previous = environment
        environment = new_environment
        yield
    finally:
        environment = previous


class Expression:
    def __str__(self) -> str:
        from interpreter.ast_printer import AstPrinter

        return AstPrinter().print(self)

    def eval(self):
        pass

    def is_truthy(self):
        return bool(self.eval())

    def run_resolver(self, resolver: Resolver):
        pass


class Binary(Expression):
    left: Expression = None
    operator: Token = None
    right: Expression = None

    def __init__(self, left: Expression, operator: Token, right: Expression) -> None:
        self.left = left
        self.operator = operator
        self.right = right

    def eval(self):
        left = self.left.eval()
        right = self.right.eval()
        operator = self.operator

        if operator.token_type == TokenType.PLUS:
            return left + right
        elif operator.token_type == TokenType.MINUS:
            return left - right
        elif operator.token_type == TokenType.STAR:
            return left * right
        elif operator.token_type == TokenType.SLASH:
            return left / right
        elif operator.token_type == TokenType.GREATER:
            return left > right
        elif operator.token_type == TokenType.GREATER_EQUAL:
            return left >= right
        elif operator.token_type == TokenType.LESS:
            return left < right
        elif operator.token_type == TokenType.LESS_EQUAL:
            return left <= right
        elif operator.token_type == TokenType.EQUAL_EQUAL:
            return left == right
        elif operator.token_type == TokenType.BANG_EQUAL:
            return left != right

    def __str__(self) -> str:
        return super().__str__()

    def run_resolver(self, resolver):
        resolver.resolve(self.left)
        resolver.resolve(self.right)


class Unary(Expression):
    operator: Token = None
    right: Expression = None

    def __init__(self, operator: Token, right: Expression) -> None:
        self.operator = operator
        self.right = right

    def eval(self):
        right: Expression = self.right.eval()
        operator: Token = self.operator

        if operator.token_type == TokenType.MINUS:
            return -right
        elif operator.token_type == TokenType.BANG:
            return not right

    def run_resolver(self, resolver):
        resolver.resolve(self.right)


class Literal(Expression):
    value: any = None

    def __init__(self, value: any) -> None:
        self.value = value

    def eval(self):
        return self.value

    def __str__(self):
        return str(self.value)

    def run_resolver(self, resolver):
        pass


class Grouping(Expression):
    expression: Expression = None

    def __init__(self, expression: Expression) -> None:
        self.expression = expression

    def eval(self):
        return self.expression.eval()

    def run_resolver(self, resolver):
        resolver.resolve(self.expression)


class Variable(Expression):
    token: Token = None

    def __init__(self, token: Token) -> None:
        self.token = token

    def eval(self):
        return lookup_variable(self.token, self)

    def __str__(self):
        return self.token.lexeme

    def run_resolver(self, resolver):
        if resolver.scopes:
            if resolver.scopes[-1].get(self.token.lexeme) is False:
                raise Exception(f"Cannot read local variable in its own initializer")

        resolver.resolve_local(self, self.token)


class Assignment(Expression):
    token: Token = None
    value: object = None

    def __init__(self, token: Token, value: object) -> None:
        self.token = token
        self.value = value

    def eval(self):
        value = self.value

        if isinstance(self.value, Expression):
            value = self.value.eval()

        distance = depth_map.get(self)
        if distance is not None:
            environment.assign_at(distance, self.token, value)
        else:
            environment.assign(self.token, value)
        return value

    def run_resolver(self, resolver):
        resolver.resolve(self.value)


class Logical(Expression):
    left: Expression = None
    operator: Token = None
    right: Expression = None

    def __init__(self, left: Expression, operator: Token, right: Expression):
        self.left = left
        self.operator = operator
        self.right = right

    def eval(self):
        left_res = self.left.eval()

        if self.operator.token_type == TokenType.OR:
            if self.left.is_truthy():
                return left_res
        else:
            # because in AND operator we return right expression only if left is falsy
            # check python in case of doubt
            if not self.left.is_truthy():
                return left_res

        return self.right.eval()

    def run_resolver(self, resolver):
        resolver.resolve(self.left)
        resolver.resolve(self.right)


class Call(Expression):
    arguments: list[Expression] = []
    callee: Expression = None
    right_paren: Token = None

    def __init__(
        self, callee: Expression, arguments: list[Expression], right_paren: Token
    ):
        self.arguments = arguments
        self.right_paren = right_paren
        self.callee = callee

    def eval(self):
        callable_obj: MyCallable = self.callee.eval()

        if not isinstance(callable_obj, MyCallable):
            raise Exception(f"{callable_obj} is not callable")

        arguments = [arg.eval() for arg in self.arguments]
        return callable_obj.call(arguments)

    def run_resolver(self, resolver):
        resolver.resolve(self.callee)

        for arg in self.arguments:
            resolver.resolve(arg)


class Get(Expression):
    name: Token = None
    object: Expression = None

    def __init__(self, object: Expression, name: Token) -> None:
        self.name = name
        self.object = object

    def eval(self):
        obj: MyInstance = self.object.eval()

        if isinstance(obj, MyInstance):
            return obj.get(self.name)

        raise Exception(f"Only instances have properties.")

    def run_resolver(self, resolver):
        resolver.resolve(self.object)


class Set(Expression):
    name: Token = None
    object: Expression = None
    value: Expression = None

    def __init__(self, object: Expression, name: Token, value: Expression) -> None:
        self.name = name
        self.object = object
        self.value = value

    def eval(self):
        obj: MyInstance = self.object.eval()

        if isinstance(obj, MyInstance):
            obj.set(self.name, self.value.eval())
            return

        raise Exception(f"Only instances have fields.")

    def run_resolver(self, resolver):
        resolver.resolve(self.value)
        resolver.resolve(self.object)


"""
program        → declaration* EOF ;

declaration    → varDecl
               | statement
               | funcDecl
               | classDecl;

statement      → exprStmt
               | printStmt
               | ifStmt
               | forStmt
               | whileStmt
               | block
               | returnStmt ;

funcDecl       → "fun" function ;
function       → IDENTIFIER "(" parameters? ")" block ;
parameters     → IDENTIFIER ( "," IDENTIFIER )* ;

classDecl      → "class" IDENTIFIER "{" function* "}" ;

exprStmt       → expression ";" ;
printStmt      → "print" expression ";" ;

varDecl        → "var" IDENTIFIER ( "=" expression )? ";" ;

block          → { (statement)? }

ifStmt         → "if" "(" expression ")" statement
               ( "else" statement )? ;

whileStmt      → "while" "(" expression ")" statement;

forStmt        → "for" "(" ( varDecl | exprStmt | ";" )
                 expression? ";"
                 expression? ")" statement ;

returnStmt     → "return" expression? ";" ;

primary        → "true" | "false" | "nil"
               | NUMBER | STRING
               | "(" expression ")"
               | IDENTIFIER ;
"""


class Statement:
    expression: Expression = None

    def __init__(self, expression: Expression) -> None:
        self.expression = expression

    def eval(self):
        pass

    def run_resolver(self, resolver: Resolver):
        pass


class PrintStatement(Statement):
    PRINT = "print"

    def eval(self):
        print(self.expression.eval())

    def run_resolver(self, resolver):
        resolver.resolve(self.expression)


class ExpressionStatement(Statement):
    def eval(self):
        return self.expression.eval()

    def run_resolver(self, resolver):
        resolver.resolve(self.expression)


class VarDeclarationStatement(Statement):
    expression: Expression = None
    token: Token = None

    def __init__(self, token: Token, expression: Expression) -> None:
        self.expression = expression
        self.token = token

    def eval(self):
        return environment.define(self.token, self.expression.eval())

    def run_resolver(self, resolver):
        resolver.declare(self.token.lexeme)
        if self.expression:
            resolver.resolve(self.expression)
        resolver.define(self.token.lexeme)


class BlockStatement(Statement):
    statements: list[Statement] = []

    def __init__(self, statements: list[Statement]):
        self.statements = statements

    def eval(self, given_environment: Environment = None):
        if given_environment is not None:
            block_environment = Environment(outer_environment=given_environment)
        else:
            block_environment = Environment(outer_environment=environment)

        # swap the environment for the execution.
        with swap_environment(block_environment):
            for stat in self.statements:
                stat.eval()

    def run_resolver(self, resolver):
        resolver.begin_scope()
        for statement in self.statements:
            resolver.resolve(statement)
        resolver.end_scope()


class IfStatement(Statement):
    condition: Expression = None
    if_statement: Statement = None
    else_statement: Statement = None

    def __init__(
        self,
        condition: Expression,
        if_statement: Statement,
        else_statement: Statement = None,
    ) -> None:
        self.condition = condition
        self.if_statement = if_statement
        self.else_statement = else_statement

    def eval(self):
        if self.condition.is_truthy():
            self.if_statement.eval()
        elif self.else_statement is not None:
            self.else_statement.eval()

    def run_resolver(self, resolver):
        resolver.resolve(self.condition)
        resolver.resolve(self.if_statement)

        if self.else_statement:
            resolver.resolve(self.else_statement)


class WhileStatement(Statement):
    condition: Expression = None
    statement: Statement = None

    def __init__(self, condition: Exception, statement: Statement):
        self.condition = condition
        self.statement = statement

    def eval(self):
        while self.condition.is_truthy():
            self.statement.eval()

    def run_resolver(self, resolver):
        resolver.resolve(self.condition)
        resolver.resolve(self.statement)


class FunctionDeclarationStatement(Statement):
    name: Token = None
    parameters: list[Token] = []
    body: BlockStatement = None

    def __init__(self, name: Token, parameters: list[Token], body: BlockStatement):
        self.name = name
        self.parameters = parameters
        self.body = body

    def eval(self):
        function = MyFunction(
            body=self.body,
            parameters=self.parameters,
            name=self.name,
            closure=environment,
        )
        environment.define(self.name, function)

    def run_resolver(self, resolver):
        resolver.declare(self.name.lexeme)
        resolver.define(self.name.lexeme)

        resolver.begin_scope()

        for param in self.parameters:
            resolver.declare(param.lexeme)
            resolver.define(param.lexeme)

        resolver.resolve(self.body)

        # end the scope
        resolver.end_scope()


class ReturnAsException(Exception):
    value: any = None

    def __init__(self, value: any) -> None:
        self.value = value


class ReturnStatement(Statement):
    expression: Expression = None
    token: Token = None

    def __init__(self, token, expression: Expression) -> None:
        self.expression = expression
        self.token = token

    def eval(self):
        value = self.expression.eval()

        raise ReturnAsException(value)

    def run_resolver(self, resolver):
        if self.expression:
            resolver.resolve(self.expression)


class ClassDeclarationStatement(Statement):
    name: Token = None
    methods: list[FunctionDeclarationStatement] = []

    def __init__(self, name: Token, methods: list[FunctionDeclarationStatement]):
        self.name = name
        self.methods = methods

    def eval(self):
        environment.define(self.name, None)
        klass = MyClass(name=self.name, methods={})

        for method in self.methods:
            klass.methods[method.name.lexeme] = method

        environment.assign(self.name, klass)

    def run_resolver(self, resolver):
        resolver.declare(self.name.lexeme)
        resolver.define(self.name.lexeme)
