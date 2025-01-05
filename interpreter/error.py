import sys


class Error:
    message = ""
    line_number = 0
    column_number = 0
    error_type = ""

    def __init__(self, error_type, message, line_number, column_number=0):
        self.error_type = error_type
        self.message = message
        self.line_number = line_number
        self.column_number = column_number

    def __str__(self):
        return f"[line {self.line_number}] Error: {self.error_type}" + (
            f": {self.message}" if self.message else ""
        )

    def print_to_stderr(self):
        print(self, file=sys.stderr)
