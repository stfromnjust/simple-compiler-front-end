from error.semantic_error import UndefinedIdentifierException, DuplicateDeclareIdentifierException
from symbol_table import SymbolTable, Symbol
from syntax import SyntaxTree, SyntaxTreeNode, BlockNode, DeclNode, ProgramNode, StmtsNode, StmtNode, LocNode, BoolNode, \
    JoinNode, EqualityNode, RelNode, ExprNode, UnaryNode, TermNode, FactorNode


class SemanticAnalyzer:
    def __init__(self, syn_tree: SyntaxTree, sym_table: SymbolTable):
        self.syn_tree = syn_tree
        self.sym_table = sym_table
        self.cur_level = -1
        self.cur_block = -1

    def analyze(self, cur_node: SyntaxTreeNode):
        skip = self.meet(cur_node)  # 继承属性
        if not skip:
            self.half(cur_node)
        self.finish(cur_node)   # 综合属性

    def meet(self, node: SyntaxTreeNode):
        if isinstance(node, ProgramNode):
            self.meet_Program(node)
            return False
        elif isinstance(node, BlockNode):
            self.meet_Block(node)
            return False
        elif isinstance(node, DeclNode):
            self.meet_Decl(node)
            return True
        elif isinstance(node, StmtsNode):
            self.meet_Stmts(node)
            return False
        elif isinstance(node, BoolNode):
            self.meet_Bool(node)
            return False
        elif isinstance(node, JoinNode):
            self.meet_Join(node)
            return False
        elif isinstance(node, EqualityNode):
            self.meet_Equality(node)
            return False
        elif isinstance(node, RelNode):
            self.meet_Rel(node)
            return False
        elif isinstance(node, ExprNode):
            self.meet_Expr(node)
            return False
        elif isinstance(node, TermNode):
            self.meet_Term(node)
            return False
        elif isinstance(node, UnaryNode):
            self.meet_Unary(node)
            return False
        elif isinstance(node, FactorNode):
            self.meet_Factor(node)
            return False
        else:
            return False

    def half(self, node):
        if isinstance(node, StmtsNode) and len(node.children) == 2:
            # Stmts -> Stmts Stmt
            self.half_Stmts(node)
        elif isinstance(node, StmtNode) and len(node.children) >= 5:
            # Stmt -> if1 ( Bool ) Stmt | while ( Bool ) Stmt | if2 ( Bool ) Stmt else Stmt
            self.half_Stmt(node)
        elif isinstance(node, BoolNode) and len(node.children) == 3:
            # Bool -> Bool || Join
            self.half_Bool(node)
        elif isinstance(node, JoinNode) and len(node.children) == 3:
            # Join -> Join && Equality
            self.half_Join(node)
        elif isinstance(node, EqualityNode) and len(node.children) == 3:
            # Equality -> Equality ==/!= Join
            self.half_Equality(node)
        elif isinstance(node, RelNode) and len(node.children) == 3:
            # Rel -> Expr <.. Expr
            self.half_Rel(node)
        elif isinstance(node, ExprNode) and len(node.children) == 3:
            # Expr -> Expr +- Term
            self.half_Expr(node)
        elif isinstance(node, TermNode) and len(node.children) == 3:
            # Term -> Term */ Unary
            self.half_Term(node)
        else:
            for child in node.children:
                self.analyze(child)

    def finish(self, node):
        if isinstance(node, BlockNode):
            self.finish_Block(node)
        elif isinstance(node, ProgramNode):
            self.finish_Program(node)
        elif isinstance(node, StmtsNode):
            self.finish_Stmts(node)
        elif isinstance(node, StmtNode):
            self.finish_Stmt(node)
        elif isinstance(node, LocNode):
            self.finish_Loc(node)
        elif isinstance(node, BoolNode):
            self.finish_Bool(node)
        elif isinstance(node, JoinNode):
            self.finish_Join(node)
        elif isinstance(node, EqualityNode):
            self.finish_Equality(node)
        elif isinstance(node, RelNode):
            self.finish_Rel(node)
        elif isinstance(node, ExprNode):
            self.finish_Expr(node)
        elif isinstance(node, TermNode):
            self.finish_Term(node)
        elif isinstance(node, UnaryNode):
            self.finish_Unary(node)
        elif isinstance(node, FactorNode):
            self.finish_Factor(node)

    def meet_Program(self, node: ProgramNode):
        node.downward()
        return

    def meet_Block(self, node: BlockNode):
        self.cur_block = self.sym_table.add_empty_table(self.cur_level, self.cur_block)
        self.cur_level += 1
        node.downward()
        return

    def meet_Decl(self, node: DeclNode):
        # Decl->Type i
        # add symbol at cur_level cur_index
        # TODO 数组情况
        name = node.children[1].val
        type = node.children[0].children[0].val
        sym = Symbol(type)
        flag = self.sym_table.add_symbol(self.cur_level, self.cur_block, name, sym)
        if not flag:
            raise DuplicateDeclareIdentifierException(name, self.cur_level, self.cur_block, node.row)
        return

    def meet_Stmts(self, node: StmtsNode):
        node.downward()
        return

    def meet_Bool(self, node: BoolNode):
        node.downward()

    def meet_Join(self, node: JoinNode):
        node.downward()

    def meet_Equality(self, node: EqualityNode):
        node.downward()

    def meet_Rel(self, node: RelNode):
        node.downward()

    def meet_Expr(self, node: ExprNode):
        node.downward()

    def meet_Term(self, node: TermNode):
        node.downward()

    def meet_Unary(self, node: UnaryNode):
        node.downward()

    def meet_Factor(self, node: FactorNode):
        node.downward()

    def half_Stmts(self, node: StmtsNode):
        # Stmts -> Stmts Stmt
        Stmts = node.children[0]
        Stmt = node.children[1]
        self.analyze(Stmts)
        Stmt.start = Stmts.start + len(Stmts.codelist)
        self.analyze(Stmt)

    def half_Stmt(self, node: StmtNode):
        # Stmt -> if1 ( Bool ) Stmt | while ( Bool ) Stmt | if2 ( Bool ) Stmt else Stmt1
        Bool = node.children[2]
        Stmt = node.children[4]
        if node.children[0].val == 'if1':
            self.analyze(Bool)
            Stmt.start = Bool.start + len(Bool.codelist)
            # 控制
            Bool.backpatch('truelist', Stmt.start)
            # 控制
            self.analyze(Stmt)
        elif node.children[0].val == 'if2':
            Stmt1 = node.children[6]
            self.analyze(Bool)
            Stmt.start = Bool.start + len(Bool.codelist)
            Bool.backpatch('truelist', Stmt.start)
            self.analyze(Stmt)
            Stmt1.start = Stmt.start + len(Stmt.codelist) + 1
            Bool.backpatch('falselist', Stmt1.start)
            self.analyze(Stmt1)

        elif node.children[0].val == 'while':
            self.analyze(Bool)
            Stmt.start = Bool.start + len(Bool.codelist)
            # 控制
            Stmt.backpatch('nextlist', Bool.start)
            Bool.backpatch('truelist', Stmt.start)
            # 控制
            self.analyze(Stmt)

    def half_Bool(self, node: BoolNode):
        # Bool -> Bool || Join
        Bool = node.children[0]
        Join = node.children[2]
        self.analyze(Bool)
        Join.start = Bool.start + len(Bool.codelist)
        # 控制
        # Bool.falselist 用 Join.start填
        if node.control:
            Bool.backpatch('falselist', Join.start)
        # 控制
        self.analyze(Join)

    def half_Join(self, node: JoinNode):
        # Join -> Join && Equality
        Join = node.children[0]
        Equality = node.children[2]
        self.analyze(Join)
        Equality.start = Join.start + len(Join.codelist)
        # 控制
        if node.control:
            Join.backpatch('truelist', Equality.start)
        # 控制
        self.analyze(Equality)

    def half_Equality(self, node: EqualityNode):
        # Equality -> Equality ==/!= Rel
        Equality = node.children[0]
        Rel = node.children[2]
        self.analyze(Equality)
        Rel.start = Equality.start + len(Equality.codelist)
        self.analyze(Rel)

    def half_Rel(self, node: RelNode):
        # Rel -> Expr </>/<=/>= Expr
        Expr1 = node.children[0]
        Expr2 = node.children[2]
        self.analyze(Expr1)
        Expr2.start = Expr1.start + len(Expr1.codelist)
        self.analyze(Expr2)

    def half_Expr(self, node: ExprNode):
        # Expr -> Expr +- Term
        Expr = node.children[0]
        Term = node.children[2]
        self.analyze(Expr)
        Term.start = Expr.start + len(Expr.codelist)
        self.analyze(Term)

    def half_Term(self, node: TermNode):
        # Term -> Term */ Unary
        Term = node.children[0]
        Unary = node.children[2]
        self.analyze(Term)
        Unary.start = Term.start + len(Term.codelist)
        self.analyze(Unary)

    def finish_Program(self, node: ProgramNode):
        node.upward()
        return

    def finish_Block(self, node: BlockNode):
        self.cur_block = self.sym_table.out[(self.cur_level, self.cur_block)]
        self.cur_level -= 1
        node.upward()

    def finish_Stmts(self, node: StmtsNode):
        node.upward()

    def finish_Stmt(self, node: StmtNode):
        node.upward()

    def finish_Loc(self, node: LocNode):
        # Loc->id  查询id的类型
        id_name = node.children[0].val
        type, level, index = self.sym_table.get_type(self.cur_level, self.cur_block, id_name)
        if type == '_':
            raise UndefinedIdentifierException(id_name, self.cur_level, self.cur_block, node.row)
        node.upward(type, level, index)

    def finish_Bool(self, node: BoolNode):
        # Bool -> Join
        if len(node.children) == 1:
            node.upward()
        # Bool -> Bool || Join
        else:
            add_name, add_level, add_block = self.sym_table.add_temp_symbol(self.cur_level, self.cur_block, Symbol('bool'))
            node.upward(add_name, add_level, add_block)

    def finish_Join(self, node: JoinNode):
        # Join -> Equality
        if len(node.children) == 1:
            node.upward()
        # Join -> Join & Equality
        else:
            add_name, add_level, add_block = self.sym_table.add_temp_symbol(self.cur_level, self.cur_block, Symbol('bool'))
            node.upward(add_name, add_level, add_block)

    def finish_Equality(self, node: EqualityNode):
        # Equality -> Rel
        if len(node.children) == 1:
            node.upward()
        # Equality -> Equality ==/!= Rel
        else:
            add_name, add_level, add_block = self.sym_table.add_temp_symbol(self.cur_level, self.cur_block, Symbol('bool'))
            node.upward(add_name, add_level, add_block)

    def finish_Rel(self, node: RelNode):
        # Rel -> Expr
        if len(node.children) == 1:
            node.upward()
        # Rel -> Expr < Expr
        else:
            add_name, add_level, add_block = self.sym_table.add_temp_symbol(self.cur_level, self.cur_block, Symbol('bool'))
            node.upward(add_name, add_level, add_block)

    def finish_Expr(self, node: ExprNode):
        flag = node.update_type()
        if flag:
            add_name, add_level, add_block = self.sym_table.add_temp_symbol(self.cur_level, self.cur_block, Symbol(node.type))
            node.upward(add_name, add_level, add_block)
        else:
            node.upward()

    def finish_Term(self, node: TermNode):
        flag = node.update_type()
        if flag:
            add_name, add_level, add_block = self.sym_table.add_temp_symbol(self.cur_level, self.cur_block, Symbol(node.type))
            node.upward(add_name, add_level, add_block)
        else:
            node.upward()

    def finish_Unary(self, node: UnaryNode):
        flag = node.update_type()
        if flag:
            add_name, add_level, add_block = self.sym_table.add_temp_symbol(self.cur_level, self.cur_block, Symbol(node.type))
            node.upward(add_name, add_level, add_block)
        else:
            node.upward()

    def finish_Factor(self, node: FactorNode):
        node.upward()









