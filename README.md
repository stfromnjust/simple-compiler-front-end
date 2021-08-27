# 软件课程设计II

918106840543 孙同 NJUST

## 1. 环境

* python 3.8

## 2. 运行

* 只需运行main.py即可, 测试代码在code.txt

* 如需更改文法，请先清除action_goto.json中的内容，再运行main.py，不过可能导致语义分析失败，慎重

* log/FA_log.txt可查看自动机日志

* log/parser_log.txt可查看移进规约过程日志

* log/sym_table_log.txt可查看符号表日志

* log/syntax_tree_log.txt可查看语法树日志
---
# Simple Compiler Front-end
Sun Tong, Nanjing University of Science and Technology

This project includes **lexical analysis**, **syntax analysis** and **semantic analysis**.
## Environment
* `python 3.8`
## Code Structure
- `data_structure`: contains some required data structure(such as Token, etc)
- `error`: contains some error that may occur(such as Undefined Identifier, etc)
- `lex_rules`: contains Type-3 grammar for lexical analysis(in .txt files)
- `log`: contains debugging files(such as Syntax Tree's visualization, etc)
- `syntax_rules`: contains Type-2 grammar for syntax analysis(in .txt file)
- `FA.py`: contains code for Finite Automata(for lexical analysis)
- `action_goto.json`: contains action_goto table(for syntax analysis)
- `code.txt`: contains test code for analysis
- `lexer.py`: contains code for lexical analysis
- `my_parser.py`: contains code for syntax analysis
- `read.py`: contains code for parsing the .txt file
- `semantic.py`: contains code for semantic analysis
- `symbol_table.py`: contains code for symbol table
- `syntax.py`: contains code for Abstract Syntax Tree(AST)'s Node
- `main.py`: an example
