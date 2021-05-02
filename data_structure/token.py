class Token:

    def __init__(self, row: int, word_type: str, word: str):
        self.row = row  # 行号
        self.word_type = word_type  # 类型, e.g. keyword, constant...
        self.word = word    # 内容, e.g. int, i...

    def __str__(self):
        return 'Token({0}, {1}, {2})\n'.format(self.row, self.word_type, self.word)

    def __repr__(self):
        return self.__str__()