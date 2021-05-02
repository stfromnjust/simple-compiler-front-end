from typing import List
import copy
import json
import read
import data_structure.item
import data_structure.token
from collections import deque

from error.syntax_error import SyntaxException
from syntax import SyntaxTree, ProgramNode, BlockNode, StmtsNode, StmtNode, LocNode, BoolNode, \
    JoinNode, EqualityNode, RelNode, ExprNode, TermNode, UnaryNode, FactorNode, NormNode, DeclsNode, DeclNode


class GraphEdge(object):
    """
    LR1转换图的边

    Args:
        start_state: 边开始状态
        end_state: 边结束状态
        symbol: 边对应符号(终结符/非终结符)
    """
    def __init__(self, start_state: str, end_state: str, symbol: str):
        self.st = start_state
        self.ed = end_state
        self.sym = symbol

    def __str__(self):
        return 'Edge (' + self.st + ', ' + self.ed + ', ' + self.sym + ')\n'

    def __repr__(self):
        return 'Edge (' + self.st + ', ' + self.ed + ', ' + self.sym + ')\n'


class Lr1Parser:
    def __init__(self, file):
        self.prods, self.start_symbol, self.vns, self.vts = read.read_syntax_txt(file)
        if '' in self.vts:
            self.vts.remove('')
        self.LR1_collection = {}  # '0': item_list
        self.LR1_edges = []
        self.first_set = {}
        self.__cal_first_set()
        self.action_goto = {}
        self.node_stack = deque()
        self.tree = None

    def __cal_first_set(self):
        #  只计算Vn的first集
        for vn in self.vns:
            self.first_set[vn] = []
        # (1)
        # 添加epsilon
        derive_eps = self.__can_derive_eps()
        for vn in derive_eps:
            # 能推出epsilon
            if derive_eps[vn] == 1:
                self.first_set[vn].append('')
        # 添加a e.g. X->a...
        for prod in self.prods:
            if prod.right[0] in self.vts:
                self.first_set[prod.left].append(prod.right[0])
        # (2)
        # X->Y1Y2Y3...
        prev_first_set = {}
        while True:
            if prev_first_set == self.first_set:
                break
            prev_first_set = copy.deepcopy(self.first_set)
            for prod in self.prods:
                # 遍历 prod.right
                for sym in prod.right:
                    if sym not in self.vns:
                        break
                    if derive_eps[sym] == 1:  # 此非终结符可以退出epsilon
                        temp = set(self.first_set[prod.left]) | (set(self.first_set[sym]) - {''})
                        self.first_set[prod.left] = list(temp)
                    elif derive_eps[sym] == 0:
                        temp = set(self.first_set[prod.left]) | (set(self.first_set[sym]))
                        self.first_set[prod.left] = list(temp)
                        break
        return

    def __can_derive_eps(self):
        prods = copy.deepcopy(self.prods)
        ret = {}
        for vn in self.vns:
            ret[vn] = 2  # 0: False, 1: True, 2: Unknown
        # (2) 删除右部含有终结符的产生式
        for i in range(len(prods) - 1, -1, -1):
            if len(set(prods[i].right) & set(self.vts)) > 0:
                prods.pop(i)
        # 检查是否有全被删除的
        for vn in self.vns:
            if len([prod for prod in prods if prod.left == vn]) == 0:
                ret[vn] = 0  # False
        # 删除右部为''的产生式
        for i in range(len(prods) - 1, -1, -1):
            if len(prods[i].right) == 1 and prods[i].right[0] == '':
                ret[prods[i].left] = 1
        for i in range(len(prods) - 1, -1, -1):
            if ret[prods[i].left] == 1:
                prods.remove(prods[i])
        # (3) 
        while True:
            if len([key for key in ret if ret[key] == 2]) == 0:
                return ret
            for i in range(len(prods) - 1, -1, -1):
                if ret[prods[i].left] == 2:
                    for j in range(len(prods[i].right) - 1, -1, -1):
                        if ret[prods[i].right[j]] == 0:
                            temp = prods[i].left
                            prods.pop(i)
                            # 如果以该非终结符为左部的产生式全部被删除, 则设为0: False
                            if len([production for production in prods if production.left == temp]) == 0:
                                ret[temp] = 0
                                if len([key for key in ret if ret[key] == 2]) == 0:
                                    return ret
                            break
                        elif ret[prods[i].right[j]] == 1:
                            prods[i].right.pop(j)
                            if len(prods[i].right) == 0:
                                ret[prods[i].left] = 1
                                if len([key for key in ret if ret[key] == 2]) == 0:
                                    return ret

    def __cal_lookahead(self, item_: data_structure.item.Item):
        # e.g.  A->a.Bb, x/y   need to cal first(bx/by)
        # only for item.right[item.point_pos] is a vn
        item_right = self.prods[item_.prod_id].right
        ret = []
        for i in range(item_.point_pos + 1, len(item_right), 1):
            if item_right[i] in self.vts:
                ret.append(item_right[i])
                return ret
            elif item_right[i] in self.vns:
                # 不能推出空
                if '' not in self.first_set[item_right[i]]:
                    ret = list(set(ret) | set(self.first_set[item_right[i]]))
                    return ret
                else:
                    ret = list(set(ret) | set(self.first_set[item_right[i]]))
        ret = list(set(ret) | {item_.lookahead})
        if '' in ret:
            ret.remove('')
        # ret is like ['a', 'b', '#']    
        return ret

    def __closure(self, item_list):
        i = -1
        while True:
            i = i + 1
            if i == len(item_list):
                break
            item_i_right = self.prods[item_list[i].prod_id].right

            if item_list[i].point_pos == len(item_i_right):
                continue
            elif item_i_right[item_list[i].point_pos] not in self.vns:
                continue
            else:
                # A->.Bsdf,t1/t2/t3
                # 添加所有 B->.xxxx, first(sdf t1,t2,t3)
                add_prod_indexes = [prod_index
                                    for prod_index in range(len(self.prods))
                                    if self.prods[prod_index].left == item_i_right[item_list[i].point_pos]
                                    ]
                lookaheads = self.__cal_lookahead(item_list[i])
                add_items = []
                for prod_index in add_prod_indexes:
                    for lookahead in lookaheads:
                        add_items.append(data_structure.item.Item(prod_index, 0, lookahead))

                item_list = item_list + list(set(add_items) - set(item_list))
        return item_list

    def __go(self, item_list, sym):
        # sym in vts or vns
        ret = []
        for item_ in item_list:
            item_right = self.prods[item_.prod_id].right
            if item_.point_pos == len(item_right):
                continue
            else:
                if item_right[item_.point_pos] == sym:
                    item1 = copy.deepcopy(item_)
                    item1.point_pos += 1
                    ret.append(item1)
        return ret

    def __is_exist(self, item_list):
        # item_list项目集是否出现在所有项目集中
        # return bool, key
        for key in self.LR1_collection:
            # item_list, LR1_collection内容相同?
            intersect_len = len(list(set(item_list) & set(self.LR1_collection[key])))
            union_len = len(list(set(item_list) | set(self.LR1_collection[key])))
            if intersect_len == union_len and intersect_len == len(item_list):
                return True, key
        return False, -1

    def build_lr1_collection(self):
        init_item_list = [data_structure.item.Item(0, 0, '#')]
        self.LR1_collection['0'] = self.__closure(init_item_list)
        i = -1
        while True:
            i += 1
            if i == len(self.LR1_collection):
                break

            cur_item_list = self.LR1_collection[str(i)]
            go_syms = set()
            for item_ in cur_item_list:
                item_right = self.prods[item_.prod_id].right
                if item_.point_pos == len(item_right):
                    continue
                go_syms.add(item_right[item_.point_pos])

            for sym in go_syms:
                go_item_list = self.__go(cur_item_list, sym)
                next_item_list = self.__closure(go_item_list)
                if len(next_item_list) > 0:
                    # 判断next_item_list是否在dict的value中存在过
                    flag, key = self.__is_exist(next_item_list)
                    if not flag:
                        # 没有出现过
                        self.LR1_collection[str(len(self.LR1_collection))] = next_item_list
                        self.LR1_edges.append(GraphEdge(str(i), str(len(self.LR1_collection) - 1), sym))
                    else:
                        # 出现过
                        self.LR1_edges.append(GraphEdge(str(i), key, sym))

    def build_action_goto(self):
        #  根据LR1_edges
        for key in self.LR1_collection:
            self.action_goto[key] = {}
        for edge in self.LR1_edges:
            if edge.sym in self.vns:
                #  goto
                self.action_goto[edge.st][edge.sym] = ('goto', edge.ed)

            elif edge.sym in self.vts:
                # s
                self.action_goto[edge.st][edge.sym] = ('s', edge.ed)
        #  规约生成
        for key in self.LR1_collection:
            item_list = self.LR1_collection[key]
            for item_ in item_list:
                item_right = self.prods[item_.prod_id].right
                if item_.point_pos == len(item_right):
                    if item_.prod_id == 0:
                        self.action_goto[key][item_.lookahead] = ('acc', -1)
                    else:
                        self.action_goto[key][item_.lookahead] = ('r', item_.prod_id)
                elif item_right == ['']:
                    self.action_goto[key][item_.lookahead] = ('r', item_.prod_id)

        with open("action_goto.json", 'w', encoding='utf-8') as fp:
            json.dump(self.action_goto, fp, ensure_ascii=False)
        return

    def program(self, token_list: List[data_structure.token.Token]) -> bool:
        # state_stack 状态栈
        # symbol_stack 符号栈
        token_list.append(data_structure.token.Token(-1, '#', '#'))
        state_stack = deque()
        state_stack.append('0')
        symbol_stack = deque()
        symbol_stack.append('#')
        token_index = 0
        while True:
            # region
            # print stack debug
            print('state_stack', state_stack, file=f)
            print('*' * 10, file=f)
            print('symbol_stack', symbol_stack, file=f)
            print('*' * 10, file=f)
            # endregion
            if token_list[token_index].word_type == 'identifier' or token_list[token_index].word_type == 'constant':
                cur_symbol = token_list[token_index].word_type
                cur_token = token_list[token_index].word
            else:
                cur_symbol = token_list[token_index].word
                cur_token = cur_symbol

            if state_stack[-1] not in self.action_goto.keys() or \
                    cur_symbol not in self.action_goto[state_stack[-1]].keys():
                raise SyntaxException(token_list[token_index], state_stack[-1], cur_symbol)
                return False
            else:
                behavior, subscript = self.action_goto[state_stack[-1]][cur_symbol]
                if behavior == 's':
                    # 移进
                    state_stack.append(subscript)
                    symbol_stack.append(cur_token)
                    token_index += 1
                elif behavior == 'r':
                    # 规约 reduction, 还需考虑epsilon规约, 在这里生成语法树
                    tree_node_list = []
                    reduction_len = len(self.prods[subscript].right)
                    if self.prods[subscript].right == ['']:
                        reduction_len = 0
                        tree_node_list.append(self.make_leaf('', token_list[token_index].row))

                    for i in range(reduction_len):
                        if symbol_stack[-1] not in self.vns:
                            tree_node_list.append(self.make_leaf(symbol_stack[-1], token_list[token_index].row))
                        else:
                            tree_node_list.append(self.node_stack[-1])
                            self.node_stack.pop()

                        state_stack.pop()
                        symbol_stack.pop()

                    # goto
                    symbol_input = self.prods[subscript].left

                    tree_node = self.make_node(symbol_input, tree_node_list, token_list[token_index].row)
                    self.node_stack.append(tree_node)

                    if state_stack[-1] not in self.action_goto.keys() or \
                            symbol_input not in self.action_goto[state_stack[-1]].keys():
                        raise SyntaxException(token_list[token_index], state_stack[-1], symbol_input)
                        return False
                    else:
                        goto, goto_state = self.action_goto[state_stack[-1]][symbol_input]
                        if goto != 'goto':
                            raise SyntaxException(token_list[token_index], state_stack[-1], symbol_input)
                            return False
                        else:
                            state_stack.append(goto_state)
                            symbol_stack.append(symbol_input)
                elif behavior == 'acc':
                    root = self.node_stack[-1]
                    self.tree = SyntaxTree(root)
                    return True

    def make_leaf(self, symbol, row):
        if symbol == 'Program':
            return ProgramNode(row)
        elif symbol == 'Block':
            return BlockNode(row)
        elif symbol == 'Stmts':
            return StmtsNode(row)
        elif symbol == 'Stmt':
            return StmtNode(row)
        elif symbol == 'Loc':
            return LocNode(row)
        elif symbol == 'Bool':
            return BoolNode(row)
        elif symbol == 'Join':
            return JoinNode(row)
        elif symbol == 'Equality':
            return EqualityNode(row)
        elif symbol == 'Rel':
            return RelNode(row)
        elif symbol == 'Expr':
            return ExprNode(row)
        elif symbol == 'Term':
            return TermNode(row)
        elif symbol == 'Unary':
            return UnaryNode(row)
        elif symbol == 'Factor':
            return FactorNode(row)
        elif symbol == 'Decls':
            return DeclsNode(row)
        elif symbol == 'Decl':
            return DeclNode(row)
        else:
            return NormNode(row, symbol)

    def make_node(self, symbol, tree_node_list, row):
        tree_node = self.make_leaf(symbol, row)
        tree_node_list.reverse()
        for child in tree_node_list:
            child.father = tree_node
            tree_node.children.append(child)
        return tree_node


f = open('log/parser_log.txt', 'w')
