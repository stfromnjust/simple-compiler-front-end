import FA as FA
from data_structure.token import Token
from error.lex_error import UnExpectedCharException


class Lexer:

    def __init__(self, dfa: FA.FA):
        self.keywords = ['if1', 'if2', 'else', 'while', 'break', 'true', 'false', 'int', 'bool', 'float']
        self.dfa = dfa  # 自动机
        self.token_list = []    # 输出Token序列
    
    def analysis(self, file):
        f = open(file, encoding="utf-8")
        cur_row = 0
        while True:
            line = f.readline()
            cur_row += 1
            if line:
                line = ' '.join(line.split()) + ' '
                if len(line) <= 1:
                    continue
                ptr = 0     # 当前指针
                cur_state = self.dfa.start_state
                token_word = ''
                while ptr < len(line):
                    nxt_state, is_valid = self.dfa.forward(cur_state, str(line[ptr]))
                    if is_valid:
                        token_word += line[ptr]
                        ptr += 1
                        cur_state = nxt_state
                    else:
                        is_final_state, state_type = self.dfa.check_state(nxt_state)
                        if not is_final_state:
                            raise UnExpectedCharException(cur_row, line[ptr])
                        if line[ptr] == ' ':
                            ptr += 1
                        if state_type == 'identifier':
                            if token_word in self.keywords:
                                state_type = 'keyword'
                        
                        self.token_list.append(Token(cur_row, state_type, token_word))
                        cur_state = self.dfa.start_state
                        token_word = ''
            else:
                break
