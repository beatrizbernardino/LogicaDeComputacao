from distutils.log import error
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
        self.origin = self.origin.replace(" ", '')

    def selectNext(self):

        if self.position >= len(self.origin):

            self.actual = Token(' ', "EOF")
            return self.actual

        elif self.origin[self.position] == '+':

            self.position += 1
            self.actual = Token('+', 'PLUS')
            return self.actual

        elif self.origin[self.position] == '-':

            self.position += 1
            self.actual = Token('-', 'MINUS')
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


class Parser:

    tokens = None

    def parseExpression():

        token = Parser.tokens.selectNext()
        resultado = 0

        if token.type == 'INT':
            resultado = token.value
            token = Parser.tokens.selectNext()

            while token.type == 'PLUS' or token.type == 'MINUS':
                if token.type == 'PLUS':
                    token = Parser.tokens.selectNext()

                    if token.type == 'INT':
                        resultado += token.value
                    else:
                        raise ValueError('Invalid Token')
                elif token.type == 'MINUS':
                    token = Parser.tokens.selectNext()
                    if token.type == 'INT':
                        resultado -= token.value
                    else:
                        raise ValueError('Invalid Token')
                token = Parser.tokens.selectNext()
            return resultado
        else:
            raise ValueError('Invalid Code')

    def run(code):
        Parser.tokens = Tokenizer(code)
        return Parser.parseExpression()


Parser.run(' 244 -4- 1 ')
