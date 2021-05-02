from data_structure.token import Token


class SyntaxException(Exception):

    def __init__(self, token: Token, state, symbol):
        self.token = token
        self.state = '_'
        self.symbol = '_'

    def __str__(self):
        return 'Syntax Exception at {0}.See more in \'log\\parser_log.txt\' and \'action_goto.json\''\
            .format(self.token)


