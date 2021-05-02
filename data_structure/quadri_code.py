import re


class QuadriCode:
    def __init__(self, op, arg1, arg2, res):
        self.op = op
        self.arg1 = arg1
        self.arg2 = arg2
        self.res = res
        self.arg1_level = -1    # arg1对应符号表中的位置
        self.arg1_index = -1
        self.arg2_level = -1    # arg2对应符号表中的位置
        self.arg2_index = -1
        self.res_level = -1     # res对应符号表中的位置
        self.res_index = -1
        self.rule = re.compile('^[a-zA-Z].*$')  # 是否有必要注明其位置

    def update(self, arg1_info, arg2_info, res_info):
        self.arg1_level, self.arg1_index = arg1_info
        self.arg2_level, self.arg2_index = arg2_info
        self.res_level, self.res_index = res_info

    def __str__(self):
        ret = 'Code\t(' + self.op + ',\t' + str(self.arg1) + ',\t' + str(self.arg2) + ',\t' + str(self.res) + ')'
        # if self.rule.match(self.arg1):
        #     ret += 'arg1_level: ' + str(self.arg1_level) + '\targ1_index: ' + str(self.arg1_index) + '\n'
        # if self.rule.match(self.arg2):
        #     ret += 'arg2_level: ' + str(self.arg2_level) + '\targ2_index: ' + str(self.arg2_index) + '\n'
        # if self.rule.match(self.res):
        #     ret += 'res_level: ' + str(self.res_level) + '\tres_index: ' + str(self.res_index) + '\n'
        return ret

    def __repr__(self):
        return self.__str__()