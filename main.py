from distutils.log import error
from multiprocessing.sharedctypes import Value
from os import execlp
import sys


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

        resultado = Parser.parseTerm()

        while Parser.tokens.actual.type == 'PLUS' or Parser.tokens.actual.type == 'MINUS':

            if Parser.tokens.actual.type == 'PLUS':
                Parser.tokens.selectNext()

                resultado += Parser.parseTerm()

            elif Parser.tokens.actual.type == 'MINUS':
                Parser.tokens.selectNext()
                resultado -= Parser.parseTerm()

            else:
                raise ValueError('Invalid Token')

        return resultado

    def parseFactor():

        resultado = 0

        if Parser.tokens.actual.type == 'INT':
            resultado = Parser.tokens.actual.value
            # Parser.tokens.selectNext()
        elif Parser.tokens.actual.type == 'PLUS' or Parser.tokens.actual.type == 'MINUS':
            Parser.tokens.selectNext()
            Parser.parseFactor()

        elif Parser.tokens.actual.type == 'OPEN_PAR':
            Parser.tokens.selectNext()
            resultado = Parser.parseExpression()
            if Parser.tokens.actual.type == 'CLOSE_PAR':
                Parser.tokens.selectNext()
            else:
                raise ValueError('Não fechou Parenteses')
        else:
            raise ValueError('Invalid Expression')
        return resultado

    def parseTerm():
        resultado = 0

        # if Parser.tokens.actual.type == 'INT':
        #     resultado = Parser.tokens.actual.value
        #     Parser.tokens.selectNext()
        resultado = Parser.parseFactor()

        while Parser.tokens.actual.type == 'MULT' or Parser.tokens.actual.type == 'DIV':
            if Parser.tokens.actual.type == 'MULT':
                Parser.tokens.selectNext()

                if Parser.tokens.actual.type == 'INT':
                    resultado *= Parser.tokens.actual.value
                else:
                    raise ValueError('Invalid Token')
            elif Parser.tokens.actual.type == 'DIV':
                Parser.tokens.selectNext()

                if Parser.tokens.actual.type == 'INT':
                    resultado //= Parser.tokens.actual.value
                else:
                    raise ValueError('Invalid Token')
            Parser.tokens.selectNext()
        return resultado
        # else:
        #     raise ValueError('Invalid Code')

    def run(code):
        if code[0] == ' ' and (code[1] == "+" or code[1] == "-" or code[1] == "*" or code[1] == "/"):

            raise ValueError('Invalid Code')

        if code[0] == ' ' and (code[1] == "+" or code[1] == "-" or code[1] == "*" or code[1] == "/") or ('+' not in code and '-' not in code and '*' not in code and '/' not in code):

            raise ValueError('Invalid Code')

        code = code.replace(" ", '')

        PrePro.code = code

        PrePro.filter()

        Parser.tokens = Tokenizer(PrePro.code)
        Parser.tokens.selectNext()
        return Parser.parseExpression()


print(Parser.run(sys.argv[1]))
