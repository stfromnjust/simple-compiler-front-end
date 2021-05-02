class Item:

    def __init__(self, prod_id: int, point_pos: int, lookahead: str):
        self.prod_id = prod_id      # 产生式编号
        self.point_pos = point_pos  # 点位置
        self.lookahead = lookahead  # lookahead, 单字符

    def __str__(self):
        return 'Item: prod_id: {0}, point_pos: {1}, lookahead: {2}\n'\
            .format(str(self.prod_id), str(self.point_pos), self.lookahead)

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return self.prod_id == other.prod_id and \
               self.point_pos == other.point_pos and \
               self.lookahead == other.lookahead

    def __hash__(self):
        return hash((self.prod_id, self.point_pos, self.lookahead))
