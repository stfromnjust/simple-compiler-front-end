from data_structure.token import Token


class SemanticException(Exception):
    def __init__(self, row, token: Token = None):
        self.row = row
        self.token = token

    def __str__(self):
        return 'Semantic Exception: {0}'.format(self.token)


class UndefinedIdentifierException(SemanticException):
    def __init__(self, id_name, level, block, row):
        super().__init__(row)
        self.id_name = id_name
        self.level = level
        self.block = block

    def __str__(self):
        return 'Undefined Identifier: {0} at row {1},\ncan\'t be found from sym_table(level={2}, index={3})'\
            .format(self.id_name, self.row, self.level, self.block) + '\nSee more in \'log\\sym_table_log.txt\''


class UnaryOperatorException(SemanticException):
    def __init__(self, op, id_name, id_type, row):
        super().__init__(row)
        self.op = op
        self.id_name = id_name
        self.id_type = id_type

    def __str__(self):
        return 'Illegal Unary Op at row {0}.\n'.format(self.row) \
            + 'Op \'{0}\' can\'t be used on \'{1}\', whose type is \'{2}\''.format(self.op, self.id_name, self.id_type)


class DuplicateDeclareIdentifierException(SemanticException):
    def __init__(self, id_name, level, index, row):
        super().__init__(row)
        self.id_name = id_name
        self.level = level
        self.index = index

    def __str__(self):
        return 'Duplicate Declare Identifier ar row {0}.\n'.format(self.row) \
            + '\'{0}\' is already declared before, in sym_table(level={1}, index={2})'\
            .format(self.id_name, self.level, self.index) + '\nSee more in \'log\\sym_table_log.txt\''
