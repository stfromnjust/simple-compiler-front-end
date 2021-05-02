import read


class GraphEdge(object):

    def __init__(self, vt: str, ed: str):
        self.vt = vt    # 边上终结符
        self.ed = ed  # 边指向状态

    def __str__(self):
        if self.vt == '':
            return 'epsilon to ' + self.ed
        return self.vt + ' to ' + self.ed

    def __repr__(self):
        return self.__str__()


class FA:
    """
    自动机

    Args:
        states_info: 所有状态及状态转换函数, states_info is like this:
            {'state_name': [GraphEdge1, GraphEdge2, ...]
             'state_name': [GraphEdge1, GraphEdge3, ...]}
        alphabet: 字母表, List[str]
        start_state: 开始状态, str
        final_states: 所有结束状态, final_states is like this:
            [[1, 2, 3],   # 1,2,3识别串1
            [4, 5, 6],    # 4,5,6识别串2
            [7, 8, 9]]   # 7,8,9识别串3
        type_list: 对应结束状态的状态名称, len(type_list) == len(final_states)
    """
    def __init__(self):
        self.states_info = {}
        self.alphabet = []
        self.start_state = None
        self.final_states = []
        self.type_list = []

    def __str__(self):
        ret = ''
        ret += 'alphabet: {0}\n'.format(str(self.alphabet))
        ret += 'states_info: '
        for key in self.states_info:
            ret += 'key: {0} value: {1}\n'.format(key, str(self.states_info[key]))
        ret += 'start_state: {0}\n'.format(self.start_state)
        ret += 'final_states: {0}\n'.format(str(self.final_states))
        ret += 'type_list: {0}\n'.format(str(self.type_list))
        return ret

    def __repr__(self):
        return self.__str__()

    def prod_build_nfa(self, file: str, word_type: str):
        """
        根据产生式文件(.txt)生成识别自动机NFA

        Args:
            file: 产生式文件(.txt)
            word_type: 该自动机识别的类型
        """
        prods, self.start_state, vns, vts = read.read_lex_txt(file)
        # create states_info
        for vn in vns:
            self.states_info[vn] = []
        self.states_info[word_type + '_final'] = []
        self.final_states.append([word_type + '_final'])
        self.type_list.append(word_type)
        # create alphabet
        for vt in vts:
            self.alphabet.append(vt)
        # create graph
        for prod_type, prod in prods:
            if prod_type == 1:
                # S->a type1
                self.states_info[prod['S']].append(GraphEdge(prod['a'], word_type + '_final'))
            elif prod_type == 2:
                # S->aB type2
                self.states_info[prod['S']].append(GraphEdge(prod['a'], prod['B']))
            elif prod_type == 3:
                # A->a type3
                self.states_info[prod['A']].append(GraphEdge(prod['a'], word_type + '_final'))
            elif prod_type == 4:
                # A->aB type4
                self.states_info[prod['A']].append(GraphEdge(prod['a'], prod['B']))

    def edge_build_fa(self, state_list, edges, start_state, final_states, type_list):
        """
        根据状态表, 边表等基本信息生成自动机

        Args:
            state_list: 所有状态列表, List[str]
            edges: 边表, List[Tuple[start_state, vt, end_state]]
            start_state: 开始状态, str
            final_states: 所有结束状态
            type_list: 对应结束状态的状态名称
        """
        for state in state_list:
            self.states_info[state] = []
        self.start_state = start_state
        self.final_states = final_states

        for final_state in final_states:
            for state in final_state:
                self.states_info[state] = []

        self.alphabet = []
        for st, vt, ed in edges:
            self.states_info[st].append(GraphEdge(vt, ed))
            if vt != '' and vt not in self.alphabet:
                self.alphabet.append(vt)

        self.type_list = type_list

    def e_closure(self, state_list):
        """
        根据状态列表求其epsilon闭包

        Args:
            state_list: 状态表, List[str]

        Returns:
            闭包状态表, List[str]
        """
        cur_states = state_list
        next_states = state_list
        while True:
            for state in cur_states:
                extend_states = [edge.ed for edge in self.states_info[state] if edge.vt == '']
                next_states = list(set(next_states) | set(extend_states))
            if len(next_states) == len(cur_states):
                break
            cur_states = next_states
        return cur_states

    def move(self, state_list, action):
        """
        求状态列表move action后的新状态列表

        Args:
            state_list: 状态表, List[str]
            action: 终结符或非终结符, str

        Returns:
            新状态表, List[str]

        """
        ret_states = []
        for state in state_list:
            extend_states = [edge.ed for edge in self.states_info[state] if edge.vt == action]
            ret_states = list(set(ret_states) | set(extend_states))
        return ret_states

    def trans_dfa(self):
        """
        将nfa转换为dfa
        """
        subset_list = []  # 子集表
        if self.start_state is None:
            return
        t = set(self.e_closure([self.start_state]))
        subset_list.append(t)
        mark = [False]  # 标记列表
        state_list = ['0']  # 新的状态列表
        edge_list = []  # 新的边表
        start_state = '0'
        final_states = []
        type_list = self.type_list  # type_list不变
        for i in range(len(type_list)):
            final_states.append([])

        while False in mark:  # 有尚未被标记的子集
            cur_t_index = mark.index(False)
            mark[cur_t_index] = True
            t = subset_list[cur_t_index]
            for alpha in self.alphabet:
                u = set(self.e_closure(self.move(list(t), alpha)))
                # 闭包为空
                if len(u) == 0:
                    continue
                if u not in subset_list:
                    subset_list.append(u)
                    mark.append(False)
                    state_list.append(str(len(mark) - 1))
                    # 是否是终态
                    # u和这些是否交集
                    for i in range(len(self.final_states)):
                        if len(set(self.final_states[i]) & u) > 0:
                            final_states[i].append(str(len(mark) - 1))
                    edge_list.append((str(cur_t_index), alpha, str(len(mark) - 1)))
                else:
                    edge_list.append((str(cur_t_index), alpha, str(subset_list.index(u))))

        self.states_info.clear()
        self.alphabet = []
        self.start_state = None
        self.final_states = []
        self.edge_build_fa(state_list, edge_list, start_state, final_states, type_list)
        return

    def merge(self, nfa):
        """
        将当前nfa与另一个nfa合并
        Args:
            nfa: 另一个nfa

        Notes:
            思想, 添加一个新的开始状态, epsilon指向两个nfa的开始态
            两个states_info字典并起来
            两个alphabet做并集
            start_state取名为两个start_state相加
            final_state做并集
        """
        self.states_info.update(nfa.states_info)
        self.alphabet = list(set(self.alphabet) | set(nfa.alphabet))
        self.states_info[self.start_state + '_' + nfa.start_state] = []
        self.states_info[self.start_state + '_' + nfa.start_state].append(GraphEdge('', self.start_state))
        self.states_info[self.start_state + '_' + nfa.start_state].append(GraphEdge('', nfa.start_state))
        self.start_state = self.start_state + '_' + nfa.start_state
        self.final_states = self.final_states + nfa.final_states
        self.type_list = self.type_list + nfa.type_list
        return

    def forward(self, state, vt):
        """
        从某状态通过某终结符的边到达另一状态

        Args:
            state: 出发状态
            vt: 经过边上的终结符

        Returns:
            如果无此终结符的边可走, 返回出发状态, False. 否则, 返回到达状态, True
        """
        # state出发的所有路径为vt的GraphEdge
        # 只能用于dfa
        edges = [edge for edge in self.states_info[state] if edge.vt == vt]
        if len(edges) == 0:
            if len(vt) == 1 and vt.isalpha():
                vt = 'letter'
                return self.forward(state, vt)
            elif len(vt) == 1 and vt.isdigit():
                vt = 'digit'
                return self.forward(state, vt)
            return state, False
        else:
            return edges[0].ed, True

    def check_state(self, state):
        """
        检查状态是否为终结状态, 并返回对应类型

        Args:
            state: 检查状态

        Returns:
            是否为终结状态, 对应类型
        """
        for index in range(len(self.final_states)):
            if state in self.final_states[index]:
                return True, self.type_list[index]
        return False, 'no_type'
