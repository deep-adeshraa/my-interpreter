class Resolver:
    scopes = []

    def resolve(self, statement):
        statement.run_resolver(self)

    def begin_scope(self):
        self.scopes.append({})

    def end_scope(self):
        self.scopes.pop()

    def declare(self, name: str):
        if not self.scopes:
            return

        scope = self.scopes[-1]
        if name in scope:
            raise Exception(
                f"Variable with name '{name}' already declared in this scope"
            )

        scope[name] = False

    def define(self, name: str):
        if not self.scopes:
            return

        scope = self.scopes[-1]
        scope[name] = True

    def resolve_local(self, expr, name):
        from interpreter.grammar import resolve as set_depth

        for i in range(len(self.scopes) - 1, -1, -1):
            if name.lexeme in self.scopes[i]:
                set_depth(expr, len(self.scopes) - 1 - i)
                return
