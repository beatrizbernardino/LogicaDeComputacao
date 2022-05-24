from distutils.log import error
from mmap import ALLOCATIONGRANULARITY
from multiprocessing.sharedctypes import Value
from os import execlp
import sys
import json
from xml.dom.minidom import Identified


class Node:

    valor = 0

    def __init__(self, value, children):

        self.value = value
        self.children = children
        self.id = Node.newId()

    def newId():
        Node.valor += 1
        return Node.valor

    def evaluate(self):
        pass


class Assembler:

    code = ""
    open('program.asm', 'w').close()
    with open('header.txt') as f:
        code = f.read()

    def write(cmd):
        Assembler.code += cmd + '\n'

    def dump():
        with open('footer.txt') as f:
            Assembler.code += f.read()

        file = open("program.asm", "a")
        file.write(Assembler.code)
        file.close()


class NoOp(Node):

    def evaluate(self):
        pass


class IntVal(Node):
    def evaluate(self):
        Assembler.write("MOV EBX, {0}".format(self.value))
        return (self.value, "INT")


class StrVal(Node):
    def evaluate(self):
        Assembler.write("MOV EBX, {0}".format(self.value))
        return (self.value, "STR")


class VarDec(Node):

    def evaluate(self):

        for child in self.children:

            SymbolTable.create(child, self.value)
            Assembler.write("PUSH DWORD 0")


class UnOp(Node):
    def evaluate(self):

        c0 = self.children[0].evaluate()

        if(c0[1] == "INT"):

            if self.value == '+':
                Assembler.write("MOV EAX, {0}".format(c0))
                return (c0, "INT")
            elif self.value == '-':
                Assembler.write("MOV EAX, {0}".format(-c0))
                return (-c0, "INT")
            elif self.value == "!":
                Assembler.write("MOV EAX, {0}".format(not c0))

                return (not c0, "INT")

        else:
            raise ValueError('UnOp')


class BinOp(Node):
    def evaluate(self):

        c0 = self.children[0].evaluate()
        Assembler.write("PUSH EBX")

        c1 = self.children[1].evaluate()
        Assembler.write("POP EAX")

        # if(c0[1] == c1[1]):

        #     if(c0[1] == "INT"):

        if self.value == '+':
            Assembler.write("ADD EAX, EBX")
            Assembler.write("MOV EBX, EAX")

            return (c0[0]+c1[0], "INT")
        elif self.value == '-':
            Assembler.write("SUB EAX, EBX")
            Assembler.write("MOV EBX, EAX")

            return (c0[0] - c1[0], "INT")
        elif self.value == '*':
            Assembler.write("IMUL EBX")
            Assembler.write("MOV EBX, EAX")

            return (c0[0] * c1[0], "INT")
        elif self.value == '/':
            Assembler.write("IDIV EBX")
            Assembler.write("MOV EBX, EAX")

            return (c0[0] // c1[0], "INT")
        elif self.value == '||':
            Assembler.write("OR EAX, EBX")

            return (int(c0[0] or c1[0]), "INT")
        elif self.value == '&&':
            Assembler.write("AND EAX, EBX")

            return (int(c0[0] and c1[0]), "INT")
        elif self.value == '==':
            Assembler.write("CMP EAX, EBX")
            Assembler.write("CALL binop_je")

            return (int(c0[0] == c1[0]), "INT")
        elif self.value == '>':
            Assembler.write("CMP EAX, EBX")
            Assembler.write("CALL binop_jg")

            return (int(c0[0] > c1[0]), "INT")
        elif self.value == '<':
            Assembler.write("CMP EAX, EBX")
            Assembler.write("CALL binop_jl")

            # return (int(c0[0] < c1[0]), c0[1])
            # elif self.value == '.':
            # return (str(c0[0])+str(c1[0]), "STRING")

            # elif(c0[1] == "STR"):
            #     if self.value == '==':
            #         return (int(c0[0] == c1[0]), c0[1])
            #     elif self.value == '>':
            #         return (int(c0[0] > c1[0]), c0[1])
            #     elif self.value == '<':
            #         return (int(c0[0] < c1[0]), c0[1])
            #     elif self.value == '.':
            #         return (str(c0[0])+str(c1[0]), "STRING")

        # else:
        #     if self.value == '.':

        #         return (str(c0[0])+str(c1[0]), "STRING")

        else:
            raise ValueError(
                "operation invalid with type of variable - BinOp")


class Block(Node):
    def evaluate(self):
        for child in self.children:
            child.evaluate()


class SymbolTable:

    dicionario = {}
    stack = 0

    def getter(chave):

        if chave in dict.keys(SymbolTable.dicionario):

            return SymbolTable.dicionario[chave]
        else:
            raise ValueError("Key not in dict")

    def setter(chave, valor):

        if chave in dict.keys(SymbolTable.dicionario):

            if valor[1] == SymbolTable.dicionario[chave][1]:

                novo_valor = (valor[0], valor[1],
                              SymbolTable.dicionario[chave][2])

                SymbolTable.dicionario[chave] = novo_valor
            else:
                raise ValueError("Wrong type declaration - SymbolTable")

        else:
            raise ValueError()

    def create(chave, tipo):

        if chave not in dict.keys(SymbolTable.dicionario):

            SymbolTable.stack += 4
            SymbolTable.dicionario[chave] = (None, tipo, SymbolTable.stack)
        else:
            raise ValueError("Key alread created- SB")


class Identifier(Node):
    def evaluate(self):
        stack = SymbolTable.getter(self.value)
        Assembler.write("MOV EBX, [EBP-{0}]".format(stack[2]))
        return stack


class Printf(Node):

    def evaluate(self):
        self.children[0].evaluate()
        Assembler.write("PUSH EBX")
        Assembler.write("CALL print")
        Assembler.write("POP EBX")

        # print(self.children[0].evaluate()[0])


class Scanf(Node):

    def evaluate(self):
        return (int(input()), "INT")


class While(Node):
    def evaluate(self):

        label_init = "LOOP_{0}:".format(self.id)
        label_end = "EXIT_{0}:".format(self.id)
        Assembler.write(label_init)
        self.children[0].evaluate()
        Assembler.write("CMP EBX,  False")
        Assembler.write("JE {0}".format(label_end))
        self.children[1].evaluate()
        Assembler.write("JMP {0}".format(label_init))
        Assembler.write(label_end)


class IF(Node):
    def evaluate(self):

        self.children[0].evaluate()
        Assembler.write("CMP EBX,  False")
        if len(self.children) > 2:
            Assembler.write("JE LABEL_{0}".format(self.id))
        else:
            Assembler.write("JE EXIT_{0}".format(self.id))

        self.children[1].evaluate()
        Assembler.write("JMP EXIT_{0}".format(self.id))

        if len(self.children) > 2:
            Assembler.write("LABEL_{0}:".format(self.id))
            self.children[2].evaluate()
            Assembler.write("JMP EXIT_{0}:".format(self.id))

        Assembler.write("EXIT_{0}:".format(self.id))


class Assignment(Node):
    def evaluate(self):

        SymbolTable.setter(self.children[0].value, self.children[1].evaluate())
        stack = SymbolTable.getter(self.children[0].value)[2]
        Assembler.write("MOV [EBP-{0}], EBX".format(stack))


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
                         "if", "else", "while", "int", "str"]

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
                elif candidato == "while":
                    self.actual = Token(candidato, 'WHILE')
                elif candidato == "str":
                    self.actual = Token(candidato.upper(), 'TYPE')
                elif candidato == "int":
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
Assembler.dump()
