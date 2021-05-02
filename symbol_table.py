class Symbol:
    def __init__(self, type):
        self.type = type

    def __str__(self):
        return 'Symbol(type: {0})'.format(self.type)

    def __repr__(self):
        return self.__str__()


class SymbolTable:
    temp_cnt = 1

    def __init__(self):
        self.tables = []  # [[{},{}], [{}]]
        self.out = {}  # {(level, index): index}

    def add_empty_table(self, level, index):
        total_level = len(self.tables) - 1
        if level > total_level:
            raise Exception
            return -1
        elif level == total_level:
            self.tables.append([])  # add level
            self.tables[level + 1].append({})
            self.out[(level + 1, 0)] = index
            return 0
        else:
            self.tables[level + 1].append({})
            new_index = len(self.tables[level + 1]) - 1
            self.out[(level + 1, new_index)] = index
            return new_index

    def add_symbol(self, level, index, name, sym: Symbol):
        if name not in self.tables[level][index].keys():
            self.tables[level][index][name] = sym
            return True
        else:
            return False

    def add_temp_symbol(self, level, index, sym: Symbol):
        name = '_T' + str(SymbolTable.temp_cnt)
        SymbolTable.temp_cnt += 1
        self.tables[level][index][name] = sym
        return name, level, index

    def get_type(self, level, index, name):
        while level >= 0:
            if name in self.tables[level][index].keys():
                return self.tables[level][index][name].type, level, index
            else:
                level -= 1
                if level < 0:
                    break
                index = self.out[(level + 1, index)]
        return '_', -1, -1

    def gen_str(self, level, index):
        ret = ''
        if level == len(self.tables) - 1:
            ret += '\t' * level + '{\n'
            ret += '\t' * level + 'level: ' + str(level) + '; index: ' + str(index) + '\n'
            ret += '\t' * level + str(list(self.tables[level][index])) + '\n'
            ret += '\t' * level + '}\n'
            return ret
        else:
            ret += '\t' * level + '{\n'
            ret += '\t' * level + 'level: ' + str(level) + '; index: ' + str(index) + '\n'
            ret += '\t' * level + str(list(self.tables[level][index])) + '\n'
            for key in self.out.keys():
                l, i = key
                prev = self.out[key]
                if index == prev and level + 1 == l:
                    ret += self.gen_str(l, i)

            ret += '\t' * level + '}\n'
            return ret

    def __str__(self):
        ret = ''
        level_cnt = 0
        for level_list in self.tables:
            ret += 'level ' + str(level_cnt) + ': \n'
            level_cnt += 1
            index = 0
            for dict_ in level_list:
                ret += 'dict ' + str(index) + ': \n' + str(dict_) + '\n'
                index += 1
            ret += '\n'
        return ret

    def __repr__(self):
        return self.__str__()
