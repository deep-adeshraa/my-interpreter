import interpreter.constants as constants
from interpreter.error import Error
from interpreter.internals import Token, TokenType, ReservedLexeme, ReservedLiteral


class Scanner:
    # TODO: refactor this class to make it more readable

    def __init__(self) -> None:
        self.has_errors: bool = False  # Flag to check if there are any errors
        self.line_number: int = 0  # Current line number
        self.tokens: list[Token] = []  # List of tokens
        self.print_stdout: bool = True  # Flag to check if the output should be printed

    def scan(self, file_name):
        with open(file_name) as file:
            file_contents = file.read()
            lines = file_contents.split("\n")

        self.scan_tokens(lines)
        return self.tokens

    def scan_line(self, line):
        # TODO: refactor this method to make it more readable
        current_lexeme = ""
        index = 0

        while index < len(line):
            current_lexeme = line[index]

            if index + 1 < len(line):
                double_char_lexeme = current_lexeme + line[index + 1]
            else:
                double_char_lexeme = ""

            if double_char_lexeme == ReservedLexeme.COMMENT:
                index = len(line)
                continue

            if current_lexeme == constants.SPACE or current_lexeme == constants.TAB:
                index += 1
                continue

            if double_char_lexeme in ReservedLexeme.DOUBLE_CHAR_LEXEMES:
                self.add_token(
                    ReservedLexeme.LEXEME_TOKEN_TYPE_MAP[double_char_lexeme],
                    double_char_lexeme,
                    ReservedLexeme.NULL,
                )
                index += 2
            elif current_lexeme in ReservedLexeme.SINGLE_CHAR_LEXEMES:
                self.add_token(
                    ReservedLexeme.LEXEME_TOKEN_TYPE_MAP[current_lexeme],
                    current_lexeme,
                    ReservedLexeme.NULL,
                )
                index += 1
            elif current_lexeme == '"':
                index = self.scan_string(line, index + 1)
            elif current_lexeme.isdigit():
                index = self.scan_number(line, index)
            elif current_lexeme.isalpha() or current_lexeme == "_":
                index = self.scan_identifier(line, index)
            else:
                self.add_error("Unexpected character", current_lexeme)
                index += 1

    def scan_string(self, line, index):
        literal = ""
        end_found = False

        while index < len(line):
            current_token = line[index]

            if current_token == '"':
                end_found = True
                break

            literal += current_token
            index += 1

        if not end_found:
            self.add_error("Unterminated string.")
            return index + 1

        lexeme = f'"{literal}"'
        self.add_token(TokenType.STRING, lexeme, literal)
        return index + 1

    def scan_number(self, line, index):
        number = ""
        dot_found = False

        while index < len(line):
            current_token = line[index]

            if current_token.isdigit():
                number += current_token
            elif current_token == "." and not dot_found:
                number += current_token
                dot_found = True
            else:
                break

            index += 1

        self.add_token(TokenType.NUMBER, number, float(number))
        return index

    def scan_identifier(self, line, index):
        identifier = ""

        while index < len(line):
            current_token = line[index]

            if current_token.isalnum() or current_token == "_":
                identifier += current_token
            else:
                break

            index += 1

        if identifier in ReservedLexeme.RESERVED_WORDS:
            if identifier in ReservedLexeme.BOOLEAN_LEXEMES:
                if identifier == "true":
                    literal = True
                elif identifier == "false":
                    literal = False
                else:
                    literal = None
                self.add_token(
                    identifier.upper(),
                    identifier,
                    literal,
                )
            else:
                self.add_token(identifier.upper(), identifier, ReservedLiteral.NULL)
        else:
            self.add_token(TokenType.IDENTIFIER, identifier, ReservedLiteral.NULL)
        return index

    def add_token(self, token_type, lexeme, literal):
        self.tokens.append(Token(token_type, lexeme, literal, self.line_number))

    def add_error(self, error_type, message=""):
        err = Error(error_type, message, self.line_number)
        err.print_to_stderr()
        self.has_errors = True

    def scan_tokens(self, lines):
        for index, line in enumerate(lines):
            self.line_number = index + 1
            self.scan_line(line)
        self.add_token(TokenType.EOF, "", ReservedLiteral.NULL)

    def close(self):
        if self.has_errors:
            exit(65)
