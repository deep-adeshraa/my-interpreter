from interpreter.internals import Token


class Environment:
    def __init__(self, outer_environment=None) -> None:
        self.values: dict = {}
        self.outer_environment: Environment = outer_environment
        self.define_default_functions()

    def define_default_functions(self):
        from interpreter.callable import ClockCallable
        from interpreter.internals import TokenType

        self.define(Token(TokenType.IDENTIFIER, "clock", None, 0), ClockCallable())

    def define(self, token: Token, value: object):
        self.values[token.lexeme] = value
        return value

    def assign(self, token: Token, value: object):
        if self.has_key(token) and token.lexeme in self.values:
            self.define(token, value)
        elif self.outer_environment and self.outer_environment.has_key(token):
            self.outer_environment.assign(token, value)
        else:
            self.raise_undefined_variable_error(token)

        return value

    def assign_at(self, distance: int, token: Token, value: object):
        self.ancestor(distance).values[token.lexeme] = value
        return value

    def has_key(self, token: Token):
        if token.lexeme in self.values:
            return True
        elif self.outer_environment:
            return self.outer_environment.has_key(token)
        return False

    def raise_undefined_variable_error(self, token: Token):
        raise Exception(
            f"Undefined variable {token.lexeme} on line {token.line_number}"
        )

    def get(self, token: Token):
        if self.has_key(token) and token.lexeme in self.values:
            return self.values[token.lexeme]
        if self.outer_environment and self.outer_environment.has_key(token):
            return self.outer_environment.get(token)

        return self.raise_undefined_variable_error(token)

    def get_at(self, distance: int, token: Token):
        return self.ancestor(distance).values[token.lexeme]

    def ancestor(self, distance: int):
        environment = self
        for _ in range(distance):
            environment = environment.outer_environment
        return environment
