from distutils.log import error
from mmap import ALLOCATIONGRANULARITY
from multiprocessing.sharedctypes import Value
from os import execlp
import sys
import json
from xml.dom.minidom import Identified


class Node:

    def __init__(self, value, children):

        self.value = value
        self.children = children

    def evaluate(self, st):
        pass


class NoOp(Node):

    def evaluate(self, st):
        pass


class IntVal(Node):
    def evaluate(self, st):
        return (self.value, "INT")


class StrVal(Node):
    def evaluate(self, st):
        return (self.value, "STR")


class Return(Node):
    def evaluate(self, st):

        return self.children[0].evaluate(st)


class VarDec(Node):

    def evaluate(self, st):

        for child in self.children:

            st.create(child, self.value)


class FuncDec(Node):

    def evaluate(self, st):

        FuncTable.create(self.children[0].value, self)


class FuncCall(Node):

    def evaluate(self, st):
        st_ = SymbolTable()

        nos = FuncTable.getter(self.value)

        chaves = []
        # print(self.children)
        for i in range(1, len(nos.children)-1):
            nos.children[i].evaluate(st_)
            nome = nos.children[i].children[0]

            chaves.append(nome)

        for child in range(1, len(chaves)+1):
            # print(chaves[child])
            a = self.children[child].evaluate(st)
            st_.setter(chaves[child-1], a)

        return nos.children[-1].evaluate(st_)


class UnOp(Node):
    def evaluate(self, st):

        c0 = self.children[0].evaluate(st)

        if(c0[1] == "INT"):

            if self.value == '+':
                return (c0, "INT")
            elif self.value == '-':
                return (-c0, "INT")
            elif self.value == "!":
                return (not c0, "INT")

        else:
            raise ValueError('UnOp')


class BinOp(Node):
    def evaluate(self, st):

        c0 = self.children[0].evaluate(st)
        c1 = self.children[1].evaluate(st)

        if(c0[1] == c1[1]):

            if(c0[1] == "INT"):

                if self.value == '+':
                    return (c0[0]+c1[0], c0[1])
                elif self.value == '-':
                    return (c0[0] - c1[0], c0[1])
                elif self.value == '*':
                    return (c0[0] * c1[0], c0[1])
                elif self.value == '/':
                    return (c0[0] // c1[0], c0[1])
                elif self.value == '||':
                    return (int(c0[0] or c1[0]), c0[1])
                elif self.value == '&&':
                    return (int(c0[0] and c1[0]), c0[1])
                elif self.value == '==':
                    return (int(c0[0] == c1[0]), c0[1])
                elif self.value == '>':
                    return (int(c0[0] > c1[0]), c0[1])
                elif self.value == '<':
                    return (int(c0[0] < c1[0]), c0[1])
                elif self.value == '.':
                    return (str(c0[0])+str(c1[0]), "STRING")

            elif(c0[1] == "STR"):
                if self.value == '==':
                    return (int(c0[0] == c1[0]), c0[1])
                elif self.value == '>':
                    return (int(c0[0] > c1[0]), c0[1])
                elif self.value == '<':
                    return (int(c0[0] < c1[0]), c0[1])
                elif self.value == '.':
                    return (str(c0[0])+str(c1[0]), "STRING")

        else:
            if self.value == '.':

                return (str(c0[0])+str(c1[0]), "STRING")

            else:
                raise ValueError(
                    "operation invalid with type of variable - BinOp")


class Block(Node):
    def evaluate(self, st):
        for child in self.children:
            if child.value == "return":
                return child.evaluate(st)
            child.evaluate(st)


class SymbolTable:

    def __init__(self):

        self.dicionario = {}

    def getter(self, chave):

        if chave in dict.keys(self.dicionario):

            return self.dicionario[chave]
        else:
            raise ValueError("Key not in dict")

    def setter(self, chave, valor):

        if chave in dict.keys(self.dicionario):

            # print("aaa", chave, valor)

            if valor[1] == self.dicionario[chave][1]:

                novo_valor = (valor[0], valor[1])

                self.dicionario[chave] = novo_valor
            else:
                raise ValueError("Wrong type declaration - SymbolTable")

        else:
            raise ValueError()

    def create(self, chave, tipo):

        if chave not in dict.keys(self.dicionario):

            self.dicionario[chave] = (None, tipo)
        else:
            raise ValueError("Key alread created- SB")


class FuncTable:

    dicionario = {}

    def getter(chave):

        if chave in dict.keys(FuncTable.dicionario):

            return FuncTable.dicionario[chave]
        else:
            raise ValueError("Key not in dict")

    # def setter(chave, valor):

    #     if chave in dict.keys(FuncTable.dicionario):

    #         if valor[1] == FuncTable.dicionario[chave][1]:

    #             novo_valor = (valor[0], valor[1])

    #             FuncTable.dicionario[chave] = novo_valor
    #         else:
    #             raise ValueError("Wrong type declaration - FuncTable")

    #     else:
    #         raise ValueError()

    def create(chave, tipo):

        if chave not in dict.keys(FuncTable.dicionario):

            FuncTable.dicionario[chave] = tipo

        else:
            raise ValueError("Key alread created- SB")


class Identifier(Node):
    def evaluate(self, st):
        return st.getter(self.value)


class Printf(Node):

    def evaluate(self, st):
        print(self.children[0].evaluate(st)[0])


class Scanf(Node):

    def evaluate(self, st):
        return (int(input()), "INT")


class While(Node):
    def evaluate(self, st):
        while self.children[0].evaluate(st)[0]:
            self.children[1].evaluate(st)


class IF(Node):
    def evaluate(self, st):
        if self.children[0].evaluate(st):
            self.children[1].evaluate(st)
        elif len(self.children) > 2:
            self.children[2].evaluate(st)


class Assignment(Node):
    def evaluate(self, st):

        st.setter(
            self.children[0].value, self.children[1].evaluate(st))


class Token:

    def __init__(self, value, type):
        self.type = type
        self.value = value


class Tokenizer:

    def __init__(self, origin):

        self.origin = origin  # '1+2+3'
        self.position = 0
        self.actual = None
        self.reserved = ["printf", "scanf",
                         "if", "else", "while", "int", "str", "return", "void"]

    def selectNext(self):

        if self.position >= len(self.origin):

            self.actual = Token(' ', "EOF")
            return self.actual

        elif self.origin[self.position] == '+':

            self.position += 1
            self.actual = Token('+', 'PLUS')
            return self.actual

        elif self.origin[self.position] == '*':

            self.position += 1
            self.actual = Token('*', 'MULT')
            return self.actual

        elif self.origin[self.position] == '.':

            self.position += 1
            self.actual = Token('.', 'CONCAT')
            return self.actual
        elif self.origin[self.position] == ',':

            self.position += 1
            self.actual = Token(',', 'COMMA')
            return self.actual

        elif self.origin[self.position] == '/':

            self.position += 1
            self.actual = Token('/', 'DIV')
            return self.actual

        elif self.origin[self.position] == '-':

            self.position += 1
            self.actual = Token('-', 'MINUS')
            return self.actual

        elif self.origin[self.position] == '(':

            self.position += 1
            self.actual = Token('(', 'OPEN_PAR')
            return self.actual

        elif self.origin[self.position] == ')':

            self.position += 1
            self.actual = Token(')', 'CLOSE_PAR')
            return self.actual

        elif self.origin[self.position] == '{':

            self.position += 1
            self.actual = Token('{', 'OPEN_BRACKET')
            return self.actual

        elif self.origin[self.position] == '}':

            self.position += 1
            self.actual = Token('}', 'CLOSE_BRACKET')
            return self.actual

        elif self.origin[self.position] == ';':

            self.position += 1
            self.actual = Token(';', 'NO_OP')
            return self.actual

        elif self.origin[self.position] == '=':

            self.position += 1

            if self.origin[self.position] == '=':
                self.position += 1
                self.actual = Token('==', 'DOUBLE_EQUAL')
            else:
                self.actual = Token('=', 'EQUAL')
            return self.actual

        elif self.origin[self.position] == '|':

            self.position += 1

            if self.origin[self.position] == '|':
                self.position += 1
                self.actual = Token('||', 'OR')
                return self.actual
            else:
                raise ValueError("Invalid Token")

        elif self.origin[self.position] == '&':

            self.position += 1

            if self.origin[self.position] == '&':
                self.position += 1
                self.actual = Token('&&', 'AND')
                return self.actual
            else:
                raise ValueError("Invalid Token")

        elif self.origin[self.position] == '>':

            self.position += 1
            self.actual = Token('>', 'GREATER')
            return self.actual

        elif self.origin[self.position] == '!':

            self.position += 1
            self.actual = Token('!', 'NOT')
            return self.actual

        elif self.origin[self.position] == '<':

            self.position += 1
            self.actual = Token('<', 'LESS')
            return self.actual

        elif self.origin[self.position] == ' ' or self.origin[self.position] == '\n':

            self.position += 1
            Parser.tokens.selectNext()

        elif self.origin[self.position].isdigit():
            candidato = self.origin[self.position]

            self.position += 1

            while self.position < len(self.origin) and self.origin[self.position].isdigit():
                candidato += self.origin[self.position]
                self.position += 1

            self.actual = Token(int(candidato), 'INT')
            return self.actual

        elif self.origin[self.position].isalpha():

            candidato = self.origin[self.position]

            self.position += 1

            while self.position < len(self.origin) and (self.origin[self.position].isalpha() or self.origin[self.position].isdigit() or self.origin[self.position] == "_"):
                candidato += self.origin[self.position]
                self.position += 1

            if candidato not in self.reserved:
                self.actual = Token(candidato, 'IDENTIFIER')
                return self.actual
            else:
                if candidato == "printf":
                    self.actual = Token(candidato, 'PRINT')
                elif candidato == "scanf":
                    self.actual = Token(candidato, 'SCANF')
                elif candidato == "if":
                    self.actual = Token(candidato, 'IF')
                elif candidato == "else":
                    self.actual = Token(candidato, 'ELSE')
                elif candidato == "return":
                    self.actual = Token(candidato, 'RETURN')
                elif candidato == "while":
                    self.actual = Token(candidato, 'WHILE')
                elif candidato == "str":
                    self.actual = Token(candidato.upper(), 'TYPE')
                elif candidato == "int":
                    self.actual = Token(candidato.upper(), 'TYPE')
                elif candidato == "void":
                    self.actual = Token(candidato.upper(), 'TYPE')
                return self.actual

        elif self.origin[self.position] == '"':

            self.position += 1
            candidato = ""

            while self.origin[self.position] != '"' and self.position < len(self.origin):
                candidato += self.origin[self.position]

                self.position += 1
            self.position += 1

            self.actual = Token(candidato, "STRING")

        else:

            raise ValueError('Invalid Token')


class PrePro:
    code = None

    def filter():
        while '/*' in PrePro.code and '*/' in PrePro.code:

            index_start = PrePro.code.index('/*')
            index_end = PrePro.code.index('*/')
            PrePro.code = PrePro.code[:index_start] + PrePro.code[index_end+2:]

        if '/*' in PrePro.code and '*/' not in PrePro.code or '/*' not in PrePro.code and '*/' in PrePro.code:
            raise ValueError('Invalid format')

        return PrePro.code


class Parser:

    tokens = None

    def parseDeclaration():

        node = None

        if Parser.tokens.actual.type == "TYPE":

            node = FuncDec(Parser.tokens.actual.value, [])
            Parser.tokens.selectNext()

            if Parser.tokens.actual.type == "IDENTIFIER":

                node_iden = VarDec(Parser.tokens.actual.value, [])
                node.children.append(node_iden)
                Parser.tokens.selectNext()

                if Parser.tokens.actual.type == "OPEN_PAR":
                    Parser.tokens.selectNext()
                    while Parser.tokens.actual.type == "TYPE":
                        node_var = VarDec(Parser.tokens.actual.value, [])
                        Parser.tokens.selectNext()
                        if Parser.tokens.actual.type == "IDENTIFIER":
                            node_var.children.append(
                                Parser.tokens.actual.value)
                            Parser.tokens.selectNext()

                        if Parser.tokens.actual.type == "COMMA":
                            node.children.append(node_var)
                            Parser.tokens.selectNext()

                        else:
                            node.children.append(node_var)

                    if Parser.tokens.actual.type == "CLOSE_PAR":
                        Parser.tokens.selectNext()

                        node.children.append(Parser.parseBlock())

                    else:

                        raise ValueError("Parenteses - parseDeclaration")

                else:

                    raise ValueError("Parenteses - parseDeclaration")

            else:
                raise ValueError("Wrong type - parseDeclaration")

        else:
            raise ValueError("Wrong Declaration- parseDeclaration")

        return node

    def parseProgram():

        node = Block("", [])

        while Parser.tokens.actual.type != "EOF":
            node.children.append(Parser.parseDeclaration())

        return node

    def parseBlock():

        node = Block("", [])
        if Parser.tokens.actual.type == 'OPEN_BRACKET':

            Parser.tokens.selectNext()
            while Parser.tokens.actual.type != 'CLOSE_BRACKET':
                # print
                node.children.append(Parser.parseStatement())

            Parser.tokens.selectNext()

        else:

            raise ValueError("Estrutura errada - parseBlock")

        return node

    def parseStatement():

        node = None

        if Parser.tokens.actual.type == "NO_OP":

            node = NoOp(";", [])
            Parser.tokens.selectNext()
            return node

        elif Parser.tokens.actual.type == "TYPE":
            node = VarDec(Parser.tokens.actual.value, [])
            Parser.tokens.selectNext()

            while Parser.tokens.actual.type == "IDENTIFIER":
                node.children.append(Parser.tokens.actual.value)

                Parser.tokens.selectNext()

                if Parser.tokens.actual.type == 'COMMA':
                    Parser.tokens.selectNext()
            return node

        elif Parser.tokens.actual.type == "IDENTIFIER":

            node = Identifier(Parser.tokens.actual.value, [])
            Parser.tokens.selectNext()

            if Parser.tokens.actual.type == "EQUAL":

                Parser.tokens.selectNext()
                node = Assignment("=", [node, Parser.parseRelExpression()])

                if Parser.tokens.actual.type == "NO_OP":
                    Parser.tokens.selectNext()

                    return node
                else:
                    raise ValueError("Faltou ; - statement")

            elif Parser.tokens.actual.type == 'OPEN_PAR':

                node = FuncCall(Parser.tokens.actual.value, [])
                Parser.tokens.selectNext()
                if Parser.tokens.actual.type == 'CLOSE_PAR':
                    return node
                else:
                    while Parser.tokens.actual.type != 'CLOSE_PAR':
                        node.children.append(Parser.parseRelExpression())
                        if Parser.tokens.actual.type == 'COMMA':
                            Parser.tokens.selectNext()

                    return node

            else:
                raise ValueError("Não atribuiu nada a variável - statement")

        elif Parser.tokens.actual.type == "RETURN":

            node = Return(Parser.tokens.actual.value, [])
            Parser.tokens.selectNext()
            if Parser.tokens.actual.type == "OPEN_PAR":
                Parser.tokens.selectNext()
                node.children.append(Parser.parseRelExpression())
                if Parser.tokens.actual.type == "CLOSE_PAR":
                    Parser.tokens.selectNext()
                    return node
                else:
                    raise ValueError("Fechar parenteses- return")
            else:
                raise ValueError("Abrir parenteses- return")

        elif Parser.tokens.actual.type == "PRINT":
            # print(Parser.tokens.actual.type, Parser.tokens.actual.value)

            Parser.tokens.selectNext()

            if Parser.tokens.actual.type == 'OPEN_PAR':

                Parser.tokens.selectNext()
                node = Printf("", [Parser.parseRelExpression()])
                # Parser.tokens.selectNext()

            if Parser.tokens.actual.type == 'CLOSE_PAR':
                Parser.tokens.selectNext()

                if Parser.tokens.actual.type == "NO_OP":
                    Parser.tokens.selectNext()
                    return node
                else:
                    raise ValueError("Faltou ; - statement")
            else:
                raise ValueError('Não fechou Parenteses')

        elif Parser.tokens.actual.type == "WHILE":

            Parser.tokens.selectNext()

            if Parser.tokens.actual.type == 'OPEN_PAR':

                Parser.tokens.selectNext()
                # print(Parser.tokens.actual.value)

                node = While("", [Parser.parseRelExpression()])

            if Parser.tokens.actual.type == 'CLOSE_PAR':
                Parser.tokens.selectNext()
                node.children.append(Parser.parseStatement())
                return node

            else:
                raise ValueError('Não fechou Parenteses')

        elif Parser.tokens.actual.type == "IF":
            # print(Parser.tokens.actual.type, Parser.tokens.actual.value)

            Parser.tokens.selectNext()

            if Parser.tokens.actual.type == 'OPEN_PAR':

                Parser.tokens.selectNext()
                # print(Parser.tokens.actual.value)

                node = IF("", [Parser.parseRelExpression()])

            if Parser.tokens.actual.type == 'CLOSE_PAR':

                Parser.tokens.selectNext()
                node.children.append(Parser.parseStatement())

                if Parser.tokens.actual.type == 'ELSE':
                    Parser.tokens.selectNext()
                    node.children.append(Parser.parseStatement())

                return node

            else:
                raise ValueError('Não fechou Parenteses')

        else:
            # print(Parser.tokens.actual.type)
            node = Parser.parseBlock()
            return node

    def parseExpression():

        node = Parser.parseTerm()

        while Parser.tokens.actual.type == 'PLUS' or Parser.tokens.actual.type == 'MINUS' or Parser.tokens.actual.type == 'OR' or Parser.tokens.actual.type == 'CONCAT':

            if Parser.tokens.actual.type == 'PLUS':
                Parser.tokens.selectNext()

                node = BinOp('+', [node, Parser.parseTerm()])

            elif Parser.tokens.actual.type == 'MINUS':
                Parser.tokens.selectNext()
                node = BinOp('-', [node, Parser.parseTerm()])

            elif Parser.tokens.actual.type == 'OR':
                Parser.tokens.selectNext()
                node = BinOp('||', [node, Parser.parseTerm()])

            elif Parser.tokens.actual.type == 'CONCAT':
                Parser.tokens.selectNext()
                node = BinOp('.', [node, Parser.parseTerm()])
            else:
                raise ValueError('Invalid Token- parseExpression')

        return node

    def parseTerm():

        node = Parser.parseFactor()

        while Parser.tokens.actual.type == 'MULT' or Parser.tokens.actual.type == 'DIV' or Parser.tokens.actual.type == 'AND':

            if Parser.tokens.actual.type == 'MULT':

                Parser.tokens.selectNext()
                node = BinOp('*', [node, Parser.parseFactor()])

            elif Parser.tokens.actual.type == 'DIV':

                Parser.tokens.selectNext()
                node = BinOp('/', [node, Parser.parseFactor()])

            elif Parser.tokens.actual.type == 'AND':

                Parser.tokens.selectNext()
                node = BinOp('&&', [node, Parser.parseFactor()])

            else:
                raise ValueError('Invalid Token- parseTerm')

        return node

    def parseFactor():

        if Parser.tokens.actual.type == 'INT':
            # resultado = Parser.tokens.actual.value
            node = IntVal(Parser.tokens.actual.value, [])
            Parser.tokens.selectNext()
            return node

        elif Parser.tokens.actual.type == 'STRING':

            # resultado = Parser.tokens.actual.value
            node = StrVal(Parser.tokens.actual.value, [])
            Parser.tokens.selectNext()
            return node

        elif Parser.tokens.actual.type == 'IDENTIFIER':

            value = Parser.tokens.actual.value
            node_iden = Identifier(value, [])
            Parser.tokens.selectNext()
            # Parser.tokens.selectNext()

            if Parser.tokens.actual.type == 'OPEN_PAR':
                node = FuncCall(value, [])
                node.children.append(node_iden)
                Parser.tokens.selectNext()
                if Parser.tokens.actual.type == 'CLOSE_PAR':
                    return node
                else:
                    while Parser.tokens.actual.type != 'CLOSE_PAR':
                        node.children.append(Parser.parseRelExpression())
                        if Parser.tokens.actual.type == 'COMMA':
                            Parser.tokens.selectNext()
                    Parser.tokens.selectNext()

                    return node

            return node_iden

        elif Parser.tokens.actual.type == 'PLUS':

            Parser.tokens.selectNext()
            # resultado = Parser.parseFactor()
            node = UnOp('+', [Parser.parseFactor()])
            return node

        elif Parser.tokens.actual.type == 'MINUS':

            Parser.tokens.selectNext()
            # resultado = -Parser.parseFactor()
            node = UnOp('-', [Parser.parseFactor()])

            return node
        elif Parser.tokens.actual.type == 'NOT':

            Parser.tokens.selectNext()
            # resultado = -Parser.parseFactor()
            node = UnOp('!', [Parser.parseFactor()])

            return node

        elif Parser.tokens.actual.type == 'OPEN_PAR':

            Parser.tokens.selectNext()
            node = Parser.parseRelExpression()

            if Parser.tokens.actual.type == 'CLOSE_PAR':
                Parser.tokens.selectNext()
                return node
            else:
                raise ValueError('Não fechou Parenteses')

        elif Parser.tokens.actual.type == 'SCANF':

            Parser.tokens.selectNext()

            node = Scanf("", [])

            if Parser.tokens.actual.type == 'OPEN_PAR':

                Parser.tokens.selectNext()

                if Parser.tokens.actual.type == 'CLOSE_PAR':
                    Parser.tokens.selectNext()
                    return node
                else:
                    raise ValueError('Não fechou Parenteses')

            else:
                raise ValueError('Não fechou Parenteses')

        else:
            raise ValueError('Invalid Expression-parseFactor')
        # return node

    def parseRelExpression():

        node = Parser.parseExpression()

        while Parser.tokens.actual.type == 'DOUBLE_EQUAL' or Parser.tokens.actual.type == 'LESS' or Parser.tokens.actual.type == 'GREATER':

            if Parser.tokens.actual.type == 'DOUBLE_EQUAL':
                Parser.tokens.selectNext()

                node = BinOp('==', [node, Parser.parseExpression()])

            elif Parser.tokens.actual.type == 'LESS':
                Parser.tokens.selectNext()
                node = BinOp('<', [node, Parser.parseExpression()])

            elif Parser.tokens.actual.type == 'GREATER':
                Parser.tokens.selectNext()
                node = BinOp('>', [node, Parser.parseExpression()])

            else:
                raise ValueError('Invalid Token- parseExpression')

        return node

    def run(file):

        code = ""
        with open(file) as f:
            for line in f:

                code += line

        PrePro.code = code
        PrePro.filter()

        Parser.tokens = Tokenizer(PrePro.code)
        Parser.tokens.selectNext()

        node = Parser.parseProgram()

        if Parser.tokens.actual.type == 'EOF':
            return node
        else:
            raise ValueError('EOF')


arvore = Parser.run(sys.argv[1])
st = SymbolTable()
node = FuncCall("main", [])
arvore.children.append(node)
arvore.evaluate(st)
