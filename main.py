from distutils.log import error
from multiprocessing.sharedctypes import Value
from os import execlp
import sys
import json


class Node:

    def __init__(self, value, children):

        self.value = value
        self.children = children

    def evaluate(self):
        pass


class NoOp(Node):

    def evaluate():
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
        else:
            raise error('BinOp')


class Token:

    def __init__(self, value, type):
        self.type = type
        self.value = value


class Tokenizer:

    def __init__(self, origin):

        self.origin = origin  # '1+2+3'
        self.position = 0
        self.actual = None

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

        elif self.origin[self.position] == ' ':

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

    def parseExpression():

        # node = IntVal(Parser.tokens.actual.value, [
        #   node, Parser.parseTerm()])
        node = Parser.parseTerm()

        while Parser.tokens.actual.type == 'PLUS' or Parser.tokens.actual.type == 'MINUS':

            if Parser.tokens.actual.type == 'PLUS':
                Parser.tokens.selectNext()

                node = BinOp('+', [node, Parser.parseTerm()])

                # resultado += Parser.parseTerm()

            elif Parser.tokens.actual.type == 'MINUS':
                Parser.tokens.selectNext()
                node = BinOp('-', [node, Parser.parseTerm()])

                # resultado -= Parser.parseTerm()

            else:
                raise ValueError('Invalid Token- parseExpression')

        return node

    def parseFactor():

        # resultado = 0

        # node = None

        if Parser.tokens.actual.type == 'INT':

            # resultado = Parser.tokens.actual.value
            node = IntVal(Parser.tokens.actual.value, [])
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

        elif Parser.tokens.actual.type == 'OPEN_PAR':

            Parser.tokens.selectNext()
            node = Parser.parseExpression()

            if Parser.tokens.actual.type == 'CLOSE_PAR':
                Parser.tokens.selectNext()
                return node
            else:
                raise ValueError('Não fechou Parenteses')
        else:
            raise ValueError('Invalid Expression-parseFactor')
        # return node

    def parseTerm():

        # resultado = 0
        node = Parser.parseFactor()
        # node = IntVal(Parser.tokens.actual.value, [
        # node, Parser.parseFactor()])

        while Parser.tokens.actual.type == 'MULT' or Parser.tokens.actual.type == 'DIV':

            if Parser.tokens.actual.type == 'MULT':

                Parser.tokens.selectNext()
                node = BinOp('*', [node, Parser.parseFactor()])
                # resultado *= Parser.parseFactor()

            elif Parser.tokens.actual.type == 'DIV':

                Parser.tokens.selectNext()
                node = BinOp('/', [node, Parser.parseFactor()])
                # resultado //= Parser.parseFactor()

        return node

    def run(file):

        with open(file) as f:
            for code in f:

                PrePro.code = code

                PrePro.filter()

                Parser.tokens = Tokenizer(PrePro.code)
                Parser.tokens.selectNext()

                node = Parser.parseExpression()

                if Parser.tokens.actual.type == 'EOF':
                    return node.evaluate()
                else:
                    raise ValueError('EOF')


print(Parser.run(sys.argv[1]))
