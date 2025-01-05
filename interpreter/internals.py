class TokenType:
    # Single-character tokens
    LEFT_PAREN = "LEFT_PAREN"
    RIGHT_PAREN = "RIGHT_PAREN"
    LEFT_BRACE = "LEFT_BRACE"
    RIGHT_BRACE = "RIGHT_BRACE"
    COMMA = "COMMA"
    DOT = "DOT"
    MINUS = "MINUS"
    PLUS = "PLUS"
    SEMICOLON = "SEMICOLON"
    SLASH = "SLASH"
    STAR = "STAR"
    COMMENT = "COMMENT"

    # One or two character tokens
    BANG = "BANG"
    BANG_EQUAL = "BANG_EQUAL"
    EQUAL = "EQUAL"
    EQUAL_EQUAL = "EQUAL_EQUAL"
    GREATER = "GREATER"
    GREATER_EQUAL = "GREATER_EQUAL"
    LESS = "LESS"
    LESS_EQUAL = "LESS_EQUAL"
    AND = "AND"
    OR = "OR"

    # Literals
    IDENTIFIER = "IDENTIFIER"
    STRING = "STRING"
    NUMBER = "NUMBER"

    # Keywords
    FALSE = "FALSE"
    TRUE = "TRUE"
    NULL = "NULL"
    NIL = "NIL"
    CLASS = "CLASS"
    ELSE = "ELSE"
    PRINT = "PRINT"
    VAR = "VAR"
    IF = "IF"
    WHILE = "WHILE"
    FOR = "FOR"
    FUNCTION = "FUN"
    RETURN = "RETURN"

    # End of file
    EOF = "EOF"


class ReservedLiteral:
    NULL = "null"
    TRUE = "true"
    FALSE = "false"
    NIL = "nil"

    BOOLEAN_LITERALS = [FALSE, TRUE, NIL]


class ReservedLexeme:
    """
    What is a lexeme?

    - A lexeme is a sequence of characters in the source program that matches the pattern
    for a token and is identified by the lexical analyzer as an instance of that token.

    In the code `var x = false;`, let’s identify the **lexemes** and the **literal**:

    ### Lexemes:
    1. `var` — Keyword lexeme
    2. `x` — Identifier lexeme (name of the variable)
    3. `=` — Assignment operator lexeme
    4. `false` — Boolean literal lexeme
    5. `;` — Semicolon lexeme (used to indicate the end of the statement)

    ### Literal:
    - `false` is the **literal** in this code. It represents a fixed Boolean value in the code, meaning it’s a constant value that is directly written into the code.

    So, in this example:
    - **Lexemes** are all the smallest units with meaning: `var`, `x`, `=`, `false`, and `;`.
    - **Literal** is specifically `false`, as it is a direct constant value in the code.

    """

    LEFT_PAREN = "("
    RIGHT_PAREN = ")"
    LEFT_BRACE = "{"
    RIGHT_BRACE = "}"
    COMMA = ","
    DOT = "."
    SEMICOLON = ";"
    SLASH = "/"
    COMMENT = "//"

    BANG = "!"
    BANG_EQUAL = "!="
    EQUAL = "="
    EQUAL_EQUAL = "=="
    GREATER = ">"
    GREATER_EQUAL = ">="
    LESS = "<"
    LESS_EQUAL = "<="
    AND_OPERATOR = "&&"
    OR_OPERATOR = "||"
    MINUS = "-"
    PLUS = "+"
    STAR = "*"

    FALSE = "false"
    TRUE = "true"
    NULL = "null"
    NIL = "nil"
    CLASS = "class"
    ELSE = "else"

    # reserved words lexemes
    CLASS = "class"
    ELSE = "else"
    FOR = "for"
    FUN = "fun"
    IF = "if"
    NIL = "nil"
    OR_WORD = "or"
    PRINT = "print"
    RETURN = "return"
    SUPER = "super"
    THIS = "this"
    VAR = "var"
    WHILE = "while"
    AND_WORD = "and"

    RESERVED_WORDS = [
        AND_WORD,
        CLASS,
        ELSE,
        FALSE,
        FOR,
        FUN,
        IF,
        NIL,
        OR_WORD,
        PRINT,
        RETURN,
        SUPER,
        THIS,
        TRUE,
        VAR,
        WHILE,
    ]

    BOOLEAN_LEXEMES = [FALSE, TRUE, NIL]

    OPERATORS = [
        BANG,
        BANG_EQUAL,
        EQUAL,
        EQUAL_EQUAL,
        GREATER,
        GREATER_EQUAL,
        LESS,
        LESS_EQUAL,
        AND_OPERATOR,
        OR_OPERATOR,
        PLUS,
        MINUS,
        STAR,
    ]

    PUNCTUATION_LEXEMES = [
        LEFT_PAREN,
        RIGHT_PAREN,
        LEFT_BRACE,
        RIGHT_BRACE,
        COMMA,
        DOT,
        SEMICOLON,
        SLASH,
    ]

    SINGLE_CHAR_LEXEMES = [
        LEFT_PAREN,
        RIGHT_PAREN,
        LEFT_BRACE,
        RIGHT_BRACE,
        COMMA,
        DOT,
        SEMICOLON,
        SLASH,
        STAR,
        MINUS,
        PLUS,
        EQUAL,
        BANG,
        GREATER,
        LESS,
    ]

    DOUBLE_CHAR_LEXEMES = [
        BANG_EQUAL,
        EQUAL_EQUAL,
        GREATER_EQUAL,
        LESS_EQUAL,
        AND_OPERATOR,
        OR_OPERATOR,
    ]

    LEXEME_TOKEN_TYPE_MAP = {
        LEFT_PAREN: TokenType.LEFT_PAREN,
        RIGHT_PAREN: TokenType.RIGHT_PAREN,
        LEFT_BRACE: TokenType.LEFT_BRACE,
        RIGHT_BRACE: TokenType.RIGHT_BRACE,
        COMMA: TokenType.COMMA,
        DOT: TokenType.DOT,
        SEMICOLON: TokenType.SEMICOLON,
        SLASH: TokenType.SLASH,
        STAR: TokenType.STAR,
        MINUS: TokenType.MINUS,
        PLUS: TokenType.PLUS,
        BANG: TokenType.BANG,
        BANG_EQUAL: TokenType.BANG_EQUAL,
        EQUAL: TokenType.EQUAL,
        EQUAL_EQUAL: TokenType.EQUAL_EQUAL,
        GREATER: TokenType.GREATER,
        GREATER_EQUAL: TokenType.GREATER_EQUAL,
        LESS: TokenType.LESS,
        LESS_EQUAL: TokenType.LESS_EQUAL,
        AND_OPERATOR: TokenType.AND,
        OR_OPERATOR: TokenType.OR,
        FALSE: TokenType.FALSE,
        TRUE: TokenType.TRUE,
        NULL: TokenType.NULL,
        NIL: TokenType.NIL,
        CLASS: TokenType.CLASS,
        ELSE: TokenType.ELSE,
    }


class Token:
    token_type: str = None
    lexeme: str = None
    literal: str = None
    line_number: int = None

    def __init__(self, token_type, lexeme, literal, line_number) -> None:
        self.token_type = token_type
        self.literal = literal
        self.lexeme = lexeme
        self.line_number = line_number

    def __str__(self) -> str:
        if self.literal in ReservedLiteral.BOOLEAN_LITERALS:
            return f"{self.token_type} {self.lexeme} {ReservedLiteral.NULL}"
        return f"{self.token_type} {self.lexeme} {self.literal}"
