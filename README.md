# Status dos Testes
![git status](http://3.129.230.99/svg/beatrizbernardino/LogicaDeComputacao/)


![plot](https://github.com/beatrizbernardino/LogicaDeComputacao/blob/main/Diagrama.png)


### EBNF

```
BLOCK = "{" , { STATEMENT }, "}" ;
STATEMENT = ( λ | ASSIGNMENT | PRINT | BLOCK | WHILE | IF), ";" ;
FACTOR = NUMBER | IDENTIFIER | (("+" | "-" | "!") , FACTOR) | "(" , RELEXPRESSION , ")" | SCANF;
TERM = FACTOR, { ("*" | "/" | "&&"), FACTOR } ;
EXPRESSION = TERM, { ("+" | "-" | "||"), TERM } ;
RELEXPRESSION = EXPRESSION , {("<" | ">" | "==") , EXPRESSION } ;
WHILE = "while", "(", RELEXPRESSION ,")", STATEMENT;
IF = "if", "(", RELEXPRESSION ,")", STATEMENT, (("else", STATEMENT) | λ );
ASSIGNMENT = IDENTIFIER, "=" , EXPRESSION ;
PRINT = "printf", "(" , EXPRESSION, ")" ;
SCANF = "scanf", "(", ")" ;
IDENTIFIER = LETTER, { LETTER | DIGIT | "_" } ;
NUMBER = DIGIT , { DIGIT } ;
LETTER = ( a | ... | z | A | ... | Z ) ;
DIGIT = ( 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 0 ) ;
```
