import re

import data_structure.production


def prod_match(txt_str: str, reg: re.Pattern):
    """
    用txt_str去匹配reg

    Args:
        txt_str: 产生式文本(一行)
        reg: 正则表达式

    Returns:
        是否匹配(bool), 提取相应位置的str(dict)
    """
    reg_match = reg.match(txt_str)
    if reg_match:
        line_bits = reg_match.groupdict()
        return True, line_bits
    else:
        return False, None


# TODO improve
def read_lex_txt(file: str):
    """
    读取词法产生式(.txt), 收集产生式, 开始符, 非终结符, 终结符等信息

    Args:
        file: 文件名

    Returns:
        产生式信息(prods), 开始符(str), 非终结符(list[str]), 终结符(list[str])
    """
    f = open(file, encoding="utf-8")
    prods = []
    start_symbol = None
    vns = []
    vts = []
    while True:
        line = f.readline()
        if line:
            # S->a type1
            reg = re.compile(r'^\[(?P<S>(.*))]->\'(?P<a>(.*))\'$')
            flag, line_bits = prod_match(line, reg)
            if flag:
                prods.append((1, line_bits))
                if start_symbol is None:
                    start_symbol = line_bits['S']
                if line_bits['S'] not in vns:
                    vns.append(line_bits['S'])
                if line_bits['a'] != '' and line_bits['a'] not in vts:
                    vts.append(line_bits['a'])
                continue
            # S->aB type2
            reg = re.compile(r'^\[(?P<S>(.*))]->\'(?P<a>(.*))\'\"(?P<B>(.*))\"$')
            flag, line_bits = prod_match(line, reg)
            if flag:
                prods.append((2, line_bits))
                if start_symbol is None:
                    start_symbol = line_bits['S']
                if line_bits['S'] not in vns:
                    vns.append(line_bits['S'])
                if line_bits['B'] not in vns:
                    vns.append(line_bits['B'])
                if line_bits['a'] != '' and line_bits['a'] not in vts:
                    vts.append(line_bits['a'])
                continue
            # A->a type3
            reg = re.compile(r'^\"(?P<A>(.*))\"->\'(?P<a>(.*))\'$')
            flag, line_bits = prod_match(line, reg)
            if flag:
                prods.append((3, line_bits))
                if line_bits['A'] not in vns:
                    vns.append(line_bits['A'])
                if line_bits['a'] != '' and line_bits['a'] not in vts:
                    vts.append(line_bits['a'])
                continue
            # A->aB type4
            reg = re.compile(r'^\"(?P<A>(.*))\"->\'(?P<a>(.*))\'\"(?P<B>(.*))\"$')
            flag, line_bits = prod_match(line, reg)
            if flag:
                prods.append((4, line_bits))
                if line_bits['A'] not in vns:
                    vns.append(line_bits['A'])
                if line_bits['B'] not in vns:
                    vns.append(line_bits['B'])
                if line_bits['a'] != '' and line_bits['a'] not in vts:
                    vts.append(line_bits['a'])
                continue
        else:
            break
    f.close()
    return prods, start_symbol, vns, vts


# TODO improve
def read_syntax_txt(file: str):
    """
    读取文法产生式(.txt), 收集产生式, 开始符, 非终结符, 终结符
    Args:
        file: filename e.g. productions.txt

    Returns:
        产生式列表, 开始符(str), 非终结符(List[str]), 终结符(List[str])
    """
    f = open(file, encoding="utf-8")
    start_symbol = None
    vns = []
    vts = []
    prods = []
    while True:
        line = f.readline()
        if line:
            # []-> ...
            reg = re.compile(r'^\[(.*?)]->((\"(.*?)\")|(\'(.*?)\')|(\[(.*?)]))+$')
            reg_match = reg.match(line)
            if reg_match:
                reg = re.compile(r'^\[(?P<S>(.*?))]->(?P<remain>(.*))$')
                # 提取...
                reg_match = reg.match(line)
                line_bits = reg_match.groupdict()
                # 提取S
                if start_symbol is None:
                    start_symbol = line_bits['S']
                    vns.append(line_bits['S'])
                # 提取右侧 ' '  " " [ ]
                reg = re.compile(r'\'.*?\'|\".*?\"|\[.*?]')
                list1 = re.findall(reg, line_bits['remain'])
                list2 = []
                # 去除' ', " ", [ ]
                for symbol in list1:
                    reg = re.compile(r'^\'(?P<sym>(.*))\'$')
                    reg_match = reg.match(symbol)
                    if reg_match:
                        symbol_bits = reg_match.groupdict()
                        if symbol_bits['sym'] not in vts:
                            vts.append(symbol_bits['sym'])
                        list2.append(symbol_bits['sym'])
                        continue
                    reg = re.compile(r'^\"(?P<sym>(.*))\"$')
                    reg_match = reg.match(symbol)
                    if reg_match:
                        symbol_bits = reg_match.groupdict()
                        if symbol_bits['sym'] not in vns:
                            vns.append(symbol_bits['sym'])
                        list2.append(symbol_bits['sym'])
                        continue
                    reg = re.compile(r'^\[(?P<sym>(.*))]$')
                    reg_match = reg.match(symbol)
                    if reg_match:
                        symbol_bits = reg_match.groupdict()
                        if symbol_bits['sym'] not in vns:
                            vns.append(symbol_bits['sym'])
                        list2.append(symbol_bits['sym'])
                        continue
                prods.append(data_structure.production.Production(line_bits['S'], list2))
            else:
                # " "->...
                reg = re.compile(r'^\"(.*)\"->((\"(.*?)\")|(\'(.*?)\')|(\[(.*?)]))+$')
                reg_match = reg.match(line)
                if reg_match:
                    reg = re.compile(r'^\"(?P<A>(.*?))\"->(?P<remain>(.*))$')
                    # 提取...
                    reg_match = reg.match(line)
                    line_bits = reg_match.groupdict()
                    # 提取A
                    if line_bits['A'] not in vns:
                        vns.append(line_bits['A'])
                    # 提取右侧 ''  " " [ ]
                    reg = re.compile(r'\'.*?\'|\".*?\"|\[.*?]')
                    list1 = re.findall(reg, line_bits['remain'])
                    list2 = []
                    # 去除 ' ' " " [ ]
                    for symbol in list1:
                        reg = re.compile(r'^\'(?P<sym>(.*))\'$')
                        reg_match = reg.match(symbol)
                        if reg_match:
                            symbol_bits = reg_match.groupdict()
                            if symbol_bits['sym'] not in vts:
                                vts.append(symbol_bits['sym'])
                            list2.append(symbol_bits['sym'])
                            continue
                        reg = re.compile(r'^\"(?P<sym>(.*))\"$')
                        reg_match = reg.match(symbol)
                        if reg_match:
                            symbol_bits = reg_match.groupdict()
                            if symbol_bits['sym'] not in vns:
                                vns.append(symbol_bits['sym'])
                            list2.append(symbol_bits['sym'])
                            continue
                        reg = re.compile(r'^\[(?P<sym>(.*))]$')
                        reg_match = reg.match(symbol)
                        if reg_match:
                            symbol_bits = reg_match.groupdict()
                            if symbol_bits['sym'] not in vns:
                                vns.append(symbol_bits['sym'])
                            list2.append(symbol_bits['sym'])
                            continue
                    prods.append(data_structure.production.Production(line_bits['A'], list2))
        else:
            break
    # 转成增广文法
    prods.insert(0, data_structure.production.Production(start_symbol + '_', [start_symbol]))
    vns.insert(0, start_symbol + '_')
    start_symbol = start_symbol + '_'

    return prods, start_symbol, vns, vts

