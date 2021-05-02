from data_structure.quadri_code import QuadriCode
from error.semantic_error import UnaryOperatorException


def res_type(arg1_type, arg2_type):
    if arg1_type == 'float' or arg2_type == 'float':
        return 'float'
    elif arg1_type == 'int' or arg2_type == 'int':
        return 'int'
    else:
        return 'bool'


def res_type_1(op, arg1_type):
    if op == '!' and arg1_type == 'bool':
        return 'bool'
    if op == '-' and arg1_type != 'bool':
        return arg1_type
    else:
        return '_'


class SyntaxTreeNode:
    cnt = 0

    def __init__(self, row):
        self.id = SyntaxTreeNode.cnt
        self.father = None
        self.children = []  # SyntaxTreeNode list

        self.row = row
        SyntaxTreeNode.cnt += 1

    def __str__(self):
        ret = 'SyntaxTreeNode ' + str(self.id) + ': '
        ret += '    ' + self.__class__.__name__
        # if self.father is None:
        #     ret += '    ' + 'no father'
        # else:
        #     ret += '    ' + 'father: ' + str(self.father.id)
        # ret += '    ' + 'children: '
        # for child in self.children:
        #     ret += str(child.id) + ' '
        # ret += '    ' + 'row: ' + str(self.row)
        # ret += '    ' + 'col: ' + str(self.col)
        return ret

    def __repr__(self):
        return self.__str__()


# TODO implement

class NormNode(SyntaxTreeNode):
    def __init__(self, row, val=''):
        super().__init__(row)
        self.val = val

    def __str__(self):
        return super().__str__() + '    val: ' + str(self.val)

    def __repr__(self):
        return super().__str__() + '    val: ' + str(self.val)


class ProgramNode(SyntaxTreeNode):
    def __init__(self, row):
        super().__init__(row)
        self.codelist = []
        self.start = -1

    # 继承属性
    def downward(self):
        self.start = 0
        return

    # 综合属性
    def upward(self):
        # Program -> Block
        self.codelist = self.children[0].codelist
        return


class BlockNode(SyntaxTreeNode):
    def __init__(self, row):
        super().__init__(row)
        self.codelist = []
        self.start = -1

    def downward(self):
        self.start = self.father.start

    def upward(self):
        # Block -> { Decls Stmts }
        self.codelist = self.children[2].codelist


class StmtsNode(SyntaxTreeNode):
    def __init__(self, row):
        super().__init__(row)
        self.codelist = []
        self.start = -1
        self.nextlist = []

    def downward(self):
        self.start = self.father.start

    def upward(self):
        # Stmts ->
        if len(self.children) == 1:
            self.codelist = []
        # Stmts -> Stmts Stmt
        elif len(self.children) == 2:
            Stmts = self.children[0]
            Stmt = self.children[1]
            self.codelist = Stmts.codelist + Stmt.codelist
            Stmt.backpatch('nextlist', self.start + len(self.codelist))
            self.nextlist = Stmt.nextlist


class StmtNode(SyntaxTreeNode):
    def __init__(self, row):
        super().__init__(row)
        self.codelist = []
        self.start = -1
        self.nextlist = []

    def upward(self):
        # Stmt -> Loc = Bool ;
        if len(self.children) == 4:
            Loc = self.children[0]
            Bool = self.children[2]
            code = [QuadriCode(op='=', arg1=Bool.val, arg2='_', res=Loc.val)]
            arg1_info = (Bool.level, Bool.index)
            arg2_info = (-1, -1)
            res_info = (Loc.level, Loc.index)
            code[0].update(arg1_info, arg2_info, res_info)
            self.codelist = Bool.codelist + code
        # Stmt -> Block
        elif len(self.children) == 1:
            Block = self.children[0]
            self.codelist = Block.codelist
        # Stmt->if1 ( Bool ) Stmt
        # Stmt->while ( Bool ) Stmt
        # Stmt->if2 ( Bool ) Stmt else Stmt1
        elif len(self.children) >= 5:
            Bool = self.children[2]
            Stmt = self.children[4]
            if self.children[0].val == 'if1':
                self.nextlist = Bool.falselist + Stmt.nextlist
                self.codelist = Bool.codelist + Stmt.codelist
            elif self.children[0].val == 'if2':
                Stmt1 = self.children[6]
                self.nextlist = Stmt.nextlist + Stmt1.nextlist
                code = [QuadriCode('go_to', '_', '_', Stmt1.start + len(Stmt1.codelist))]
                Stmt.codelist = Stmt.codelist + code
                self.codelist = Bool.codelist + Stmt.codelist + Stmt1.codelist
            elif self.children[0].val == 'while':
                self.nextlist = Bool.falselist
                # Stmt最后添加代码
                code = [QuadriCode('go_to', '_', '_', Bool.start)]
                Stmt.codelist = Stmt.codelist + code
                self.codelist = Bool.codelist + Stmt.codelist

    def backpatch(self, select, code_num):
        if select == 'nextlist':
            for i in self.nextlist:
                self.codelist[i - self.start].res = code_num


class LocNode(SyntaxTreeNode):
    def __init__(self, row):
        super().__init__(row)
        self.codelist = []
        self.val = '_'
        self.type = '_'
        self.level = -1
        self.index = -1

    def upward(self, type, level, index):
        # Loc -> i
        if len(self.children) == 1:
            self.val = self.children[0].val
            self.type = type
            self.level = level
            self.index = index


class BoolNode(SyntaxTreeNode):
    def __init__(self, row):
        super().__init__(row)
        self.codelist = []
        self.val = '_'
        self.type = '_'
        self.level = -1
        self.index = -1
        self.start = -1
        self.truelist = []
        self.falselist = []
        self.control = False    # False Bool为了计算 True Bool为了控制

    def downward(self):
        self.start = self.father.start
        BoolFather = self.father
        if isinstance(BoolFather, StmtNode):
            if len(BoolFather.children) == 4:
                # BoolFather -> Loc = Bool;
                self.control = False
            else:
                self.control = True
        elif isinstance(BoolFather, BoolNode):
            self.control = BoolFather.control
        elif isinstance(BoolFather, FactorNode):
            self.control = False

    def upward(self, val='_', level='_', index='_'):
        # Bool -> Join
        if len(self.children) == 1:
            Join = self.children[0]
            self.codelist = Join.codelist
            self.val = Join.val
            self.type = Join.type
            self.level = Join.level
            self.index = Join.index
            # 控制
            if self.control:
                self.truelist = Join.truelist
                self.falselist = Join.falselist
            # 控制
        # Bool -> Bool || Join
        else:
            Bool = self.children[0]
            Op = self.children[1]
            Join = self.children[2]
            self.val = val
            self.type = 'bool'
            self.level = level
            self.index = index
            code = [QuadriCode(op=Op.val, arg1=Bool.val, arg2=Join.val, res=self.val)]
            arg1_info = (Bool.level, Bool.index)
            arg2_info = (Join.level, Join.index)
            res_info = (self.level, self.index)
            code[0].update(arg1_info, arg2_info, res_info)
            self.codelist = Bool.codelist + Join.codelist + code
            # 控制
            if self.control:
                self.truelist = Bool.truelist + Join.truelist
                self.falselist = Join.falselist
                self.codelist = Bool.codelist + Join.codelist
            # 控制

    def backpatch(self, select, code_num):
        if select == 'truelist':
            for i in self.truelist:
                self.codelist[i - self.start].res = code_num
        elif select == 'falselist':
            for i in self.falselist:
                self.codelist[i - self.start].res = code_num


class JoinNode(SyntaxTreeNode):
    def __init__(self, row):
        super().__init__(row)
        self.codelist = []
        self.val = '_'
        self.type = '_'
        self.level = -1
        self.index = -1
        self.start = -1
        self.truelist = []
        self.falselist = []
        self.control = False  # False为了计算 True为了控制

    def downward(self):
        if len(self.father.children) > 0:
            if self is self.father.children[0]:
                self.start = self.father.start
        self.control = self.father.control

    def upward(self, val='_', level='_', index='_'):
        # Join -> Equality
        if len(self.children) == 1:
            Equality = self.children[0]
            self.codelist = Equality.codelist
            self.val = Equality.val
            self.type = Equality.type
            self.level = Equality.level
            self.index = Equality.index
            if self.control:
                # 控制
                self.truelist = Equality.truelist
                self.falselist = Equality.falselist
                # 控制
        # Join -> Join && Equality
        elif len(self.children) == 3:
            Join = self.children[0]
            Op = self.children[1]
            Equality = self.children[2]
            self.val = val
            self.type = 'bool'
            self.level = level
            self.index = index
            code = [QuadriCode(op=Op.val, arg1=Join.val, arg2=Equality.val, res=self.val)]
            arg1_info = (Join.level, Join.index)
            arg2_info = (Equality.level, Equality.index)
            res_info = (self.level, self.index)
            code[0].update(arg1_info, arg2_info, res_info)
            self.codelist = Join.codelist + Equality.codelist + code
            if self.control:
                # 控制
                self.falselist = Join.falselist + Equality.falselist
                self.truelist = Equality.truelist
                self.codelist = Join.codelist + Equality.codelist
                # 控制

    def backpatch(self, select, code_num):
        if select == 'truelist':
            for i in self.truelist:
                self.codelist[i - self.start].res = code_num
        elif select == 'falselist':
            for i in self.falselist:
                self.codelist[i - self.start].res = code_num


class EqualityNode(SyntaxTreeNode):
    def __init__(self, row):
        super().__init__(row)
        self.codelist = []
        self.val = '_'
        self.type = '_'
        self.level = -1
        self.index = -1
        self.start = -1
        self.truelist = []
        self.falselist = []
        self.control = False

    def downward(self):
        # Join -> Equality
        if len(self.father.children) > 0:
            if self is self.father.children[0]:
                self.start = self.father.start
        if isinstance(self.father, JoinNode):
            self.control = self.father.control
        else:
            self.control = False

    def upward(self, val='_', level='_', index='_'):
        # Equality -> Rel
        if len(self.children) == 1:
            Rel = self.children[0]
            self.codelist = Rel.codelist
            self.val = Rel.val
            self.type = Rel.type
            self.level = Rel.level
            self.index = Rel.index
        elif len(self.children) == 3:
            # Equality -> Equality ==/!= Rel
            Equality = self.children[0]
            Op = self.children[1]
            Rel = self.children[2]
            self.val = val
            self.type = 'bool'
            self.level = level
            self.index = index
            code = [QuadriCode(op=Op.val, arg1=Equality.val, arg2=Rel.val, res=self.val)]
            arg1_info = (Equality.level, Equality.index)
            arg2_info = (Rel.level, Rel.index)
            res_info = (self.level, self.index)
            code[0].update(arg1_info, arg2_info, res_info)
            self.codelist = Equality.codelist + Rel.codelist + code

        if self.control:
            # 控制
            self.truelist = [self.start + len(self.codelist)]
            self.falselist = [self.start + len(self.codelist) + 1]
            code = [QuadriCode('if_true_go_to', self.val, '_', -1)]
            arg1_info = (self.level, self.index)
            code[0].update(arg1_info, (-1, -1), (-1, -1))
            self.codelist = self.codelist + code
            self.codelist.append(QuadriCode('go_to', '_', '_', -1))
            # 控制


class RelNode(SyntaxTreeNode):
    def __init__(self, row):
        super().__init__(row)
        self.codelist = []
        self.val = '_'
        self.type = '_'
        self.level = -1
        self.index = -1
        self.start = -1
        self.truelist = []
        self.falselist = []

    def downward(self):
        # Equality -> Rel
        if len(self.father.children) > 0:
            if self is self.father.children[0]:
                self.start = self.father.start

    def upward(self, val='_', level='_', index='_'):
        # Rel -> Expr
        if len(self.children) == 1:
            Expr = self.children[0]
            self.codelist = Expr.codelist
            self.val = Expr.val
            self.type = Expr.type
            self.level = Expr.level
            self.index = Expr.index
        elif len(self.children) == 3:
            # Rel -> Expr </<=/>/>= Expr
            Expr1 = self.children[0]
            Op = self.children[1]
            Expr2 = self.children[2]
            self.val = val
            self.type = 'bool'
            self.level = level
            self.index = index
            code = [QuadriCode(op=Op.val, arg1=Expr1.val, arg2=Expr2.val, res=self.val)]
            arg1_info = (Expr1.level, Expr1.index)
            arg2_info = (Expr2.level, Expr2.index)
            res_info = (self.level, self.index)
            code[0].update(arg1_info, arg2_info, res_info)
            self.codelist = Expr1.codelist + Expr2.codelist + code


class ExprNode(SyntaxTreeNode):
    def __init__(self, row):
        super().__init__(row)
        self.codelist = []
        self.val = '_'
        self.type = '_'
        self.level = -1
        self.index = -1
        self.start = -1
        self.truelist = []
        self.falselist = []

    def downward(self):
        if len(self.father.children) > 0:
            if self is self.father.children[0]:
                self.start = self.father.start

    def update_type(self):
        # Expr -> Term
        if len(self.children) == 1:
            Term = self.children[0]
            self.type = Term.type
            return False
        elif len(self.children) == 3:
            # Expr -> Expr +/- Term
            Expr = self.children[0]
            Term = self.children[2]
            self.type = res_type(Expr.type, Term.type)
            return True

    def upward(self, val='_', level='_', index='_'):
        # Expr -> Term
        if len(self.children) == 1:
            Term = self.children[0]
            self.codelist = Term.codelist
            self.val = Term.val
            self.level = Term.level
            self.index = Term.index
        elif len(self.children) == 3:
            # Expr -> Expr +/- Term
            Expr = self.children[0]
            Op = self.children[1]
            Term = self.children[2]
            self.val = val
            self.level = level
            self.index = index
            # self.val需要创建临时变量
            code = [QuadriCode(op=Op.val, arg1=Expr.val, arg2=Term.val, res=self.val)]
            arg1_info = (Expr.level, Expr.index)
            arg2_info = (Term.level, Term.index)
            res_info = (self.level, self.index)
            code[0].update(arg1_info, arg2_info, res_info)
            self.codelist = Expr.codelist + Term.codelist + code


class TermNode(SyntaxTreeNode):
    def __init__(self, row):
        super().__init__(row)
        self.codelist = []
        self.val = '_'
        self.type = '_'
        self.level = -1
        self.index = -1
        self.start = -1
        self.truelist = []
        self.falselist = []

    def downward(self):
        if len(self.father.children) > 0:
            if self is self.father.children[0]:
                self.start = self.father.start

    def update_type(self):
        # Term -> Unary
        if len(self.children) == 1:
            Unary = self.children[0]
            self.type = Unary.type
            return False
        # Term -> Term *// Unary
        elif len(self.children) == 3:
            Term = self.children[0]
            Unary = self.children[2]
            self.type = res_type(Term.type, Unary.type)
            return True

    def upward(self, val='_', level='_', index='_'):
        # Term -> Unary
        if len(self.children) == 1:
            Unary = self.children[0]
            self.codelist = Unary.codelist
            self.val = Unary.val
            self.level = Unary.level
            self.index = Unary.index
        elif len(self.children) == 3:
            # Term -> Term *// Unary
            Term = self.children[0]
            Op = self.children[1]
            Unary = self.children[2]
            self.val = val
            self.level = level
            self.index = index
            code = [QuadriCode(op=Op.val, arg1=Term.val, arg2=Unary.val, res=self.val)]
            arg1_info = (Term.level, Term.index)
            arg2_info = (Unary.level, Unary.index)
            res_info = (self.level, self.index)
            code[0].update(arg1_info, arg2_info, res_info)
            self.codelist = Term.codelist + Unary.codelist + code


class UnaryNode(SyntaxTreeNode):
    def __init__(self, row):
        super().__init__(row)
        self.codelist = []
        self.val = '_'
        self.type = '_'
        self.level = -1
        self.index = -1
        self.start = -1
        self.truelist = []
        self.falselist = []

    def downward(self):
        # Term -> Unary
        if len(self.father.children) == 1:
            if self is self.father.children[0]:
                self.start = self.father.start
        # Unary -> !Unary
        elif len(self.father.children) == 2:
            if self is self.father.children[1]:
                self.start = self.father.start
        # Term -> Term */ Unary escapes

    def update_type(self):
        # Unary -> Factor
        if len(self.children) == 1:
            Factor = self.children[0]
            self.type = Factor.type
            return False
        elif len(self.children) == 2:
            # Unary -> !/- Factor
            Op = self.children[0]
            Factor = self.children[1]
            self.type = res_type_1(Op.val, Factor.type)
            if self.type == '_':
                raise UnaryOperatorException(Op.val, Factor.val, Factor.type, Factor.row)
            return True

    def upward(self, val='_', level='_', index='_'):
        # Unary -> Factor
        if len(self.children) == 1:
            Factor = self.children[0]
            self.codelist = Factor.codelist
            self.val = Factor.val
            self.level = Factor.level
            self.index = Factor.index
        elif len(self.children) == 2:
            # Unary -> !/- Unary
            Op = self.children[0]
            Unary = self.children[1]
            self.val = val
            self.level = level
            self.index = index
            code = [QuadriCode(op=Op.val, arg1=Unary.val, arg2='_', res=self.val)]
            arg1_info = (Unary.level, Unary.index)
            arg2_info = (-1, -1)
            res_info = (self.level, self.index)
            code[0].update(arg1_info, arg2_info, res_info)
            self.codelist = Unary.codelist + code


class FactorNode(SyntaxTreeNode):
    def __init__(self, row):
        super().__init__(row)
        self.codelist = []
        self.val = '_'
        self.type = '_'
        self.level = -1
        self.index = -1
        self.start = -1
        self.truelist = []
        self.falselist = []

    def downward(self):
        self.start = self.father.start

    def upward(self):
        # Factor -> Loc/constant/true/false
        if len(self.children) == 1:
            Child = self.children[0]
            if isinstance(Child, LocNode):
                self.val = Child.val
                self.type = Child.type
                self.level = Child.level
                self.index = Child.index

            elif isinstance(Child, NormNode):
                self.val = Child.val
                if self.val == 'true' or self.val == 'false':
                    self.type = 'bool'
                else:
                    self.type = 'float'
        elif len(self.children) == 3:
            # Factor -> (Bool)
            Bool = self.children[1]
            self.codelist = Bool.codelist
            self.val = Bool.val
            self.type = Bool.type
            self.level = Bool.level
            self.index = Bool.index


class DeclsNode(SyntaxTreeNode):
    def __init__(self, row):
        super().__init__(row)


class DeclNode(SyntaxTreeNode):
    def __init__(self, row):
        super().__init__(row)


class SyntaxTree:
    def __init__(self, root):
        self.root = root

    def dfs(self, cur_node, cur_depth=0):
        print('\t'*cur_depth, cur_node, file=f, end='|  ')
        # if hasattr(cur_node, 'codelist'):
        #     print('codelist: ', cur_node.codelist, file=f, end='|   ')
        # else:
        #     print('', file=f, end='|    ')
        #
        # if hasattr(cur_node, 'start'):
        #     print('start', cur_node.start, file=f, end='|   ')
        # else:
        #     print('', file=f, end='|    ')
        #
        # if hasattr(cur_node, 'truelist'):
        #     print('truelist', cur_node.truelist, file=f, end='| ')
        # else:
        #     print('', file=f, end='|    ')
        #
        # if hasattr(cur_node, 'falselist'):
        #     print('falselist', cur_node.falselist, file=f, end='| ')
        # else:
        #     print('', file=f, end='|    ')

        if hasattr(cur_node, 'row'):
            print('row', cur_node.row, file=f, end='| ')
        else:
            print('', file=f, end='|    ')

        print('\n', file=f)
        for child in cur_node.children:
            self.dfs(child, cur_depth + 1)


f = open('log/syntax_tree_log.txt', 'w')
