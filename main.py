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

    def evaluate(self):
        pass


class NoOp(Node):

    def evaluate(self):
        pass


class IntVal(Node):
    def evaluate(self):
        return self.value


class UnOp(Node):
    def evaluate(self):

        if self.value == '+':
            return self.children[0].evaluate()
        elif self.value == '-':
            return - self.children[0].evaluate()
        elif self.value == "!":
            return not self.children[0].evaluate()

        else:
            raise ValueError('UnOp')


class BinOp(Node):
    def evaluate(self):

        if self.value == '+':
            return self.children[0].evaluate() + self.children[1].evaluate()
        elif self.value == '-':
            return self.children[0].evaluate() - self.children[1].evaluate()
        elif self.value == '*':
            return self.children[0].evaluate() * self.children[1].evaluate()
        elif self.value == '/':
            return self.children[0].evaluate() // self.children[1].evaluate()
        elif self.value == '==':
            return self.children[0].evaluate() == self.children[1].evaluate()
        elif self.value == '>':
            return self.children[0].evaluate() > self.children[1].evaluate()
        elif self.value == '<':
            return self.children[0].evaluate() < self.children[1].evaluate()
        elif self.value == '||':
            return self.children[0].evaluate() or self.children[1].evaluate()
        elif self.value == '&&':
            return self.children[0].evaluate() and self.children[1].evaluate()

        else:
            raise error('BinOp')


class Block(Node):
    def evaluate(self):
        for child in self.children:
            child.evaluate()


class SymbolTable:

    dicionario = {}

    def getter(chave):

        if chave in dict.keys(SymbolTable.dicionario):

            return SymbolTable.dicionario[chave]
        else:
            raise ValueError("Key not in dict")

    def setter(chave, valor):

        SymbolTable.dicionario[chave] = valor


class Identifier(Node):
    def evaluate(self):
        return SymbolTable.getter(self.value)


class Printf(Node):

    def evaluate(self):
        print(self.children[0].evaluate())


class Scanf(Node):

    def evaluate(self):
        return int(input())


class While(Node):
    def evaluate(self):
        while self.children[0].evaluate():
            self.children[1].evaluate()


class IF(Node):
    def evaluate(self):
        if self.children[0].evaluate():
            self.children[1].evaluate()
        elif len(self.children) > 2:
            self.children[2].evaluate()


class Assignment(Node):
    def evaluate(self):

        SymbolTable.setter(self.children[0].value, self.children[1].evaluate())


class Token:

    def __init__(self, value, type):
        self.type = type
        self.value = value


class Tokenizer:

    def __init__(self, origin):

        self.origin = origin  # '1+2+3'
        self.position = 0
        self.actual = None
        self.reserved = ["printf", "scanf", "if", "else", "while"]

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
                elif candidato == "while":
                    self.actual = Token(candidato, 'WHILE')
                return self.actual

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

    def parseBlock():

        node = Block("", [])

        if Parser.tokens.actual.type == 'OPEN_BRACKET':

            Parser.tokens.selectNext()
            while Parser.tokens.actual.type != 'CLOSE_BRACKET':

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

            else:
                raise ValueError("Não atribuiu nada a variável - statement")

        elif Parser.tokens.actual.type == "PRINT":
            # print(Parser.tokens.actual.type, Parser.tokens.actual.value)

            Parser.tokens.selectNext()

            if Parser.tokens.actual.type == 'OPEN_PAR':

                Parser.tokens.selectNext()
                # print(Parser.tokens.actual.value)

                node = Printf("", [Parser.parseRelExpression()])

            if Parser.tokens.actual.type == 'CLOSE_PAR':
                Parser.tokens.selectNext()

                if Parser.tokens.actual.type == "NO_OP":
                    Parser.tokens.selectNext()
                    return node
                else:
                    raise ValueError("Faltou ; - statement")
            else:
                raise ValueError('Não fechou Parenteses')

        elif Parser.tokens.actual.type == "PRINT":
            # print(Parser.tokens.actual.type, Parser.tokens.actual.value)

            Parser.tokens.selectNext()

            if Parser.tokens.actual.type == 'OPEN_PAR':

                Parser.tokens.selectNext()
                # print(Parser.tokens.actual.value)

                node = Printf("", [Parser.parseRelExpression()])

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
            # print(Parser.tokens.actual.type, Parser.tokens.actual.value)

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

        while Parser.tokens.actual.type == 'PLUS' or Parser.tokens.actual.type == 'MINUS':

            if Parser.tokens.actual.type == 'PLUS':
                Parser.tokens.selectNext()

                node = BinOp('+', [node, Parser.parseTerm()])

            elif Parser.tokens.actual.type == 'MINUS':
                Parser.tokens.selectNext()
                node = BinOp('-', [node, Parser.parseTerm()])

            elif Parser.tokens.actual.type == 'OR':
                Parser.tokens.selectNext()
                node = BinOp('||', [node, Parser.parseTerm()])

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

        if Parser.tokens.actual.type == 'IDENTIFIER':

            # resultado = Parser.tokens.actual.value

            node = Identifier(Parser.tokens.actual.value, [])
            Parser.tokens.selectNext()
            return node

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

        node = Parser.parseBlock()

        if Parser.tokens.actual.type == 'EOF':
            return node
        else:
            raise ValueError('EOF')


arvore = Parser.run(sys.argv[1])
arvore.evaluate()
