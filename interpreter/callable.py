import time
from interpreter.environment import Environment
from interpreter.internals import Token, TokenType


class MyCallable:
    def __call__(self, *args, **kwargs):
        return args, kwargs

    def call(self, arguments):
        return self(*arguments)

    def arity(self):
        return


class MyClass(MyCallable):
    name: Token = None
    methods: dict[str, MyCallable] = {}

    def __init__(self, name, methods):
        self.name = name
        self.methods = methods

    def __call__(self, *args, **kwargs):
        instance = MyInstance(self)

        init_method: MyFunction = self.methods.get("init")

        if init_method:
            init_method.bind(instance)(*args, **kwargs)

        return instance

    def arity(self):
        has_init = self.methods.get("init")
        if has_init:
            return has_init.arity()

        return 0

    def __str__(self):
        return f"<class {self.name.lexeme}>"


class MyFunction(MyCallable):
    body = None
    parameters: list[Token] = []
    name: Token = None
    closure: Environment = None

    def __init__(self, parameters, body, name, closure):
        self.parameters = parameters
        self.body = body
        self.name = name
        self.closure = closure

    def __call__(self, *args, **kwargs):
        from interpreter.grammar import ReturnAsException

        # define parameters in the function environment and create a new environment
        function_environment = Environment(outer_environment=self.closure)

        for i in range(len(self.parameters)):
            parameter = self.parameters[i]
            function_environment.define(parameter, args[i])

        try:
            self.body.eval(given_environment=function_environment)
        except ReturnAsException as e:
            if self.name.lexeme == "init":
                return self.closure.get(Token(TokenType.THIS, "this", None, 0))

            return e.value

        if self.name.lexeme == "init":
            return self.closure.get(Token(TokenType.THIS, "this", None, 0))

    def arity(self):
        return len(self.parameters)

    def bind(self, instance):
        new_closure = Environment(outer_environment=self.closure)
        # it means that replace this with the instance in new environment
        new_closure.define(
            Token(
                token_type=TokenType.THIS,
                lexeme="this",
                literal=None,
                line_number=0,
            ),
            instance,
        )
        return MyFunction(
            parameters=self.parameters,
            body=self.body,
            name=self.name,
            closure=new_closure,
        )

    def __str__(self):
        return f"<fn {self.name.lexeme}>"


class MyInstance:
    klass: MyClass = None
    fields: dict[str, any] = {}

    def __init__(self, klass: MyClass):
        self.klass = klass
        self.fields = {}

    def __str__(self):
        return f"<instance of {self.klass.name.lexeme}>"

    def get(self, name: Token):
        if name.lexeme in self.fields:
            return self.fields[name.lexeme]

        method = self.klass.methods.get(name.lexeme)

        if method:
            return method.bind(self)

        raise Exception(f"Undefined property '{name.lexeme}'.")

    def set(self, name: Token, value):
        self.fields[name.lexeme] = value


# native function clock
class ClockCallable(MyFunction):

    def __init__(self):
        super().__init__(
            parameters=[],
            body=None,
            name=Token("clock", 0, literal=None, line_number=0),
            closure=None,
        )

    def __call__(self, *args, **kwargs):
        return time.time()

    def arity(self):
        return 0

    def call(self, arguments):
        return self()
