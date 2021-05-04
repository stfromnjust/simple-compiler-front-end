import time
import json

from FA import FA
from lexer import Lexer
from my_parser import Lr1Parser
from semantic import SemanticAnalyzer
from symbol_table import SymbolTable


# 词法分析
identFA = FA()
identFA.prod_build_nfa("lex_rules/identifier.txt", 'identifier')
delimiterFA = FA()
delimiterFA.prod_build_nfa("lex_rules/delimiter.txt", 'delimiter')
operatorFA = FA()
operatorFA.prod_build_nfa("lex_rules/operator.txt", 'operator')
constantFA = FA()
constantFA.prod_build_nfa("lex_rules/constant.txt", 'constant')
identFA.merge(delimiterFA)
identFA.merge(operatorFA)
identFA.merge(constantFA)
identFA.trans_dfa()
with open('log/FA_log.txt', 'w') as f:
    print(identFA, file=f)
my_lexer = Lexer(identFA)
my_lexer.analysis("code.txt")
print('词法分析: ')
print(my_lexer.token_list)
# 词法分析

# 语法分析
test = Lr1Parser("syntax_rules\\dragon_rules.txt")
# print(test.first_set, file=data)
with open('action_goto.json', 'r', encoding='utf8') as fp:
    try:
        json_data = json.load(fp)
        test.action_goto = json_data
    except Exception as e:
        print('no data in json...')
        test.build_lr1_collection()
        test.build_action_goto()
print('语法分析: ')
print(test.program(my_lexer.token_list))
# 语法分析

# 语义分析
test1 = SemanticAnalyzer(test.tree, SymbolTable())
test1.analyze(test1.syn_tree.root)
# 打印符号表
with open('log/sym_table_log.txt', 'w') as f:
    print(test1.sym_table.gen_str(0, 0), file=f)
    print('*'*20, file=f)
    print('out:', file=f)
    print(test1.sym_table.out, file=f)
    print(test1.sym_table, file=f)
# 打印四元式序列
print('语义分析: ')
code_num = 0
for code in test1.syn_tree.root.codelist:
    print('{0}:{1}'.format(code_num, code))
    code_num += 1

# 打印语法树
test1.syn_tree.dfs(test1.syn_tree.root)
# 语义分析
