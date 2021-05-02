class Production:

    def __init__(self, left, right):
        self.left = left  # 左侧的非终结符  str
        self.right = right  # 右侧的符号序列 list(str)

    def __str__(self):
        return 'production:\nleft: {0}\nright: {1}'.format(self.left, str(self.right))

    def __repr__(self):
        return self.__str__()
