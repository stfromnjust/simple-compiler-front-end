from data_structure.token import Token


class LexException(Exception):
    def __init__(self, row=-1, char='_', token: Token = None):
        self.row = row
        self.char = char
        self.token = token

    def __str__(self):
        return 'Lex Exception: {0}'.format(self.token)


class UnExpectedCharException(LexException):
    def __init__(self, row=-1, char='_', prev=None):
        super().__init__(row, char, prev)

    def __str__(self):
        return 'UnExpected Char \'{0}\' at row {1}'.format(self.char, self.row)


