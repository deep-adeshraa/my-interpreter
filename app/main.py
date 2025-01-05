import sys
from interpreter.scanner import Scanner
from interpreter.parser import Parser
from interpreter.resolver import Resolver


def main():
    if len(sys.argv) < 3:
        print("Usage: ./your_program.sh tokenize <filename>", file=sys.stderr)
        exit(1)

    command = sys.argv[1]
    filename = sys.argv[2]

    scanner = Scanner()
    tokens = scanner.scan(filename)
    scanner.close()

    if command == "tokenize":
        for i in tokens:
            print(i)
    elif command == "parse":
        parser = Parser(tokens)
        expression = parser.parse()
        print(expression)
    elif command == "evaluate":
        scanner = Scanner()
        tokens = scanner.scan(filename)
        parser = Parser(tokens)
        statements = parser.parse()
        resolver = Resolver()

        for i in statements:
            i.run_resolver(resolver)

        for i in statements:
            i.eval()


if __name__ == "__main__":
    main()
