from enum import Enum

class Token:
    def __init__(self, pos, name, attr=None):
        self.pos = pos      # Posição (linha, coluna)
        self.name = name    # Tipo do token (TokenName)
        self.attr = attr    # Atributo adicional (TokenAttr ou valor)

    def __str__(self):
        return f"({self.name}, {self.attr}, pos={self.pos})"

class TokenName(Enum):
    # Tokens especiais
    EOF = 0
    IGNORE = 1

    # Palavras-chave
    MAIN = 10
    INICIO = 11
    FIM = 12
    CASO = 13
    ENTAO = 14
    SENAO = 15
    ENQUANTO = 16
    FACA = 17
    REPITA = 18
    ATE = 19
    TIPO = 20   # int, char, float

    # Identificador e constantes
    ID = 30
    CONST_NUM = 31
    CONST_CHAR = 32

    # Símbolos
    PAR_ESQ = 40  # (
    PAR_DIR = 41  # )
    SETA = 42     # ->
    PONTO_VIRGULA = 43  # ;
    VIRGULA = 44         # ,

    # Operadores
    RELOP = 50  # operadores relacionais (==, !=, <, >, <=, >=)
    ATRIB = 51  # =
    ADD = 52    # +
    SUB = 53    # -
    MUL = 54    # *
    DIV = 55    # /
    POW = 56    # ^

    def __str__(self):
        return self.name

class TokenAttr(Enum):
    # Operadores relacionais específicos
    EQ = 100  # ==
    NE = 101  # !=
    LT = 102  # <
    GT = 103  # >
    LE = 104  # <=
    GE = 105  # >=

    def __str__(self):
        return self.name
