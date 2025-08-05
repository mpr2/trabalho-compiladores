from Token import Token, TokenName, TokenAttr
from SymbolTable import SymbolTableEntry

class Lexer:
    def __init__(self, file_path):
        self.reader = BufReader(file_path)
        self.pos = (1,1)
        self.table = TransitionTable(self.reader)
        self.lexeme_buffer = ""
        self.buffered_token = None
        self.symbol_table = {
            "main": SymbolTableEntry(TokenName.MAIN, "main"),
            "inicio": SymbolTableEntry(TokenName.INICIO, "inicio"),
            "fim": SymbolTableEntry(TokenName.FIM, "fim"),
            "caso": SymbolTableEntry(TokenName.CASO, "caso"),
            "entao": SymbolTableEntry(TokenName.ENTAO, "entao"),
            "senao": SymbolTableEntry(TokenName.SENAO, "senao"),
            "enquanto": SymbolTableEntry(TokenName.ENQUANTO, "enquanto"),
            "faca": SymbolTableEntry(TokenName.FACA, "faca"),
            "repita": SymbolTableEntry(TokenName.REPITA, "repita"),
            "ate": SymbolTableEntry(TokenName.ATE, "ate"),
            "int": SymbolTableEntry(TokenName.TIPO, "int", type=TokenAttr.INT),
            "char": SymbolTableEntry(TokenName.TIPO, "char", type=TokenAttr.CHAR),
            "float": SymbolTableEntry(TokenName.TIPO, "float", type=TokenAttr.FLOAT),
        }

    def next_token(self):
        if self.buffered_token is not None:
            token = self.buffered_token
            self.buffered_token = None
            return token

        count = {
            'chars': 0,
            'lf': 0,
            'last_lf': -1,
        }
        s = self.table.initial()
        self.lexeme_buffer = ""  # Reinicia o buffer para o novo token
        
        while not self.table.final(s):
            c = self.reader.read_char()
            s = self.table.move(s, c)
            if c is not None:
                self.lexeme_buffer += c  # Acumula caracteres do lexema
                
        token = self.table.actions(s, self.pos, count, self.lexeme_buffer, self.symbol_table)
        self.pos = (
            self.pos[0] + count['lf'],
            self.pos[1] + count['chars'] if count['lf'] == 0 else count['chars'] - count['last_lf']
        )
        if token.name == TokenName.IGNORE:
            return self.next_token()

        return token

    def peek_token(self):
        if self.buffered_token is None:
            self.buffered_token = self.next_token()
        return self.buffered_token


class TransitionTable:
    def __init__(self, reader):
        self.reader = reader
        self.table = {
            # Estado 0: Inicial
            0: {
                ' ': 1, '\t': 1, '\n': 1, '\r': 1,  # Espaços
                '/': 3,  # Comentários ou divisão
                **{chr(i): 8 for i in range(ord('a'), ord('z')+1)},  # Letras minúsculas
                **{chr(i): 8 for i in range(ord('A'), ord('Z')+1)},  # Letras maiúsculas
                '_': 8,  # Identificadores
                **{str(i): 10 for i in range(10)},  # Dígitos
                '\'': 18,  # Char
                '=': 22,  # Atribuição/igualdade
                '!': 25,  # Diferente
                '<': 27,  # Menor/menor-igual
                '>': 30,  # Maior/maior-igual
                '(': 33,  # Parênteses esquerdo
                ')': 34,  # Parênteses direito
                ';': 38,  # Ponto e vírgula
                ',': 39,  # Vírgula
                '+': 40,  # Adição
                '*': 41,  # Multiplicação
                '^': 42,  # Potência
                '-': 35,  # Subtração/seta
                None: 100  # EOF
            },
            
            # Estado 1: Espaços
            1: {
                ' ': 1, '\t': 1, '\n': 1, '\r': 1
            },
            
            # Estado 3: Comentários (início)
            3: {
                '*': 4,
            },
            
            # Estado 4: Comentários (corpo)
            4: {
                '*': 5,
            },
            
            # Estado 5: Comentários (fim)
            5: {
                '/': 6,
                '*': 5
            },
            
            # Estado 8: Identificadores
            8: {
                **{chr(i): 8 for i in range(ord('a'), ord('z')+1)},
                **{chr(i): 8 for i in range(ord('A'), ord('Z')+1)},
                **{str(i): 8 for i in range(10)},
                '_': 8
            },
            
            # Estado 10: Números
            10: {
                **{str(i): 10 for i in range(10)},
                '.': 11,
                'E': 13, 'e': 13
            },
            
            # Estado 11: Números (após ponto)
            11: {
                **{str(i): 12 for i in range(10)}
            },
            
            # Estado 12: Números (ponto decimal)
            12: {
                **{str(i): 12 for i in range(10)},
                'E': 13, 'e': 13
            },
            
            # Estado 13: Números (expoente)
            13: {
                '+': 14, '-': 14,
                **{str(i): 15 for i in range(10)}
            },
            
            # Estado 14: Números (sinal expoente)
            14: {
                **{str(i): 15 for i in range(10)}
            },
            
            # Estado 15: Números (dígitos expoente)
            15: {
                **{str(i): 15 for i in range(10)}
            },
            
            # Estado 18: Char (aberto)
            18: {
                '\\': 21
            },
            
            # Estado 19: Char (fechamento)
            19: {
                '\'': 20
            },
            
            # Estado 21: Char (escape)
            21: {
                '\'': 19, '\\': 19
            },
            
            # Estado 22: Igualdade
            22: {
                '=': 23
            },
            
            # Estado 25: Diferente
            25: {
                '=': 26
            },
            
            # Estado 27: Menor que
            27: {
                '=': 28
            },
            
            # Estado 30: Maior que
            30: {
                '=': 31
            },
            
            # Estado 35: Subtração/Seta
            35: {
                '>': 36
            },
        }
        
        self.others = {
            0: -1,     # Caractere inválido
            1: 2,      # Fim de espaços
            3: 7,      # Divisão (não é comentário)
            4: 4,      # Continua comentário
            5: 4,      # Continua comentário
            8: 9,      # Fim de identificador
            10: 16,    # Fim de número inteiro
            11: -1,    # Ponto sem dígito (erro)
            12: 17,    # Fim de número float
            13: -1,    # Expoente sem dígito (erro)
            14: -1,    # Sinal sem dígito (erro)
            15: 17,    # Fim de número com expoente
            18: 19,    # Char normal
            19: -1,    # Char sem fechamento (erro)
            21: 19,    # Char após escape
            22: 24,    # Atribuição
            25: -1,    # sem = (erro)
            27: 29,    # Menor que
            30: 32,    # Maior que
            35: 37,    # Subtração
        }

        self.final_states = {-1, 2, 6, 7, 9, 16, 17, 20, 23, 24, 26, 28, 29, 31, 32, 33, 34, 36, 37, 38, 39, 40, 41, 42, 100}
        self.lookahead_states = {2, 7, 9, 16, 17, 24, 29, 32, 37}

    def initial(self):
        return 0

    def final(self, s):
        return s in self.final_states

    def move(self, s, c):
        if s in self.final_states:
            raise Exception("Transição inválida: estado final")

        if s not in self.table:
            raise Exception(f"Estado inválido: {s}")
        
        if c not in self.table[s]:
            return self.others[s]
        return self.table[s][c]
        
    def actions(self, s, pos, count, lexeme, symbol_table):
        if s == -1:
            raise Exception(f"Erro léxico: {pos}")

        # Estados que precisam retroceder
        if s in self.lookahead_states:
            self.reader.go_back()
            lexeme = lexeme[:-1]  # Remove último caractere (não pertence ao token)

        # Contagem de caracteres e quebras de linha pro cálculo da posição
        count['chars'] = len(lexeme)
        count['lf'] = lexeme.count('\n')
        count['last_lf'] = lexeme.rfind('\n')

        match s:
            case 2:
                return Token(pos, TokenName.IGNORE) 
            case 6:
                return Token(pos, TokenName.IGNORE) 
            case 7:
                return Token(pos, TokenName.DIV) 
            case 9:
                if lexeme not in symbol_table:
                    symbol_table[lexeme] = SymbolTableEntry(TokenName.ID, lexeme)
                    return Token(pos, TokenName.ID, lexeme) 
                entry = symbol_table[lexeme]
                if entry.name == TokenName.ID:
                    return Token(pos, entry.name, lexeme)
                return Token(pos, entry.name, entry.type)
            case 16:
                if lexeme not in symbol_table:
                    symbol_table[lexeme] = SymbolTableEntry(TokenName.CONST_NUM, lexeme, int(lexeme), TokenAttr.INT)
                return Token(pos, TokenName.CONST_NUM, lexeme) 
            case 17:
                if lexeme not in symbol_table:
                    symbol_table[lexeme] = SymbolTableEntry(TokenName.CONST_NUM, lexeme, float(lexeme), TokenAttr.FLOAT)
                return Token(pos, TokenName.CONST_NUM, lexeme) 
            case 20:
                if lexeme not in symbol_table:
                    ch = lexeme[1:-1]
                    ch = ch[1] if ch[0] == '\\' else ch[0]
                    symbol_table[lexeme] = SymbolTableEntry(TokenName.CONST_CHAR, lexeme, ch, TokenAttr.CHAR)
                return Token(pos, TokenName.CONST_CHAR, lexeme) 
            case 23:
                return Token(pos, TokenName.RELOP, TokenAttr.EQ) 
            case 24:
                return Token(pos, TokenName.ATRIB) 
            case 26:
                return Token(pos, TokenName.RELOP, TokenAttr.NE)
            case 28:
                return Token(pos, TokenName.RELOP, TokenAttr.LE) 
            case 29:
                return Token(pos, TokenName.RELOP, TokenAttr.LT) 
            case 31:
                return Token(pos, TokenName.RELOP, TokenAttr.GE) 
            case 32:
                return Token(pos, TokenName.RELOP, TokenAttr.GT) 
            case 33:
                return Token(pos, TokenName.PAR_ESQ) 
            case 34:
                return Token(pos, TokenName.PAR_DIR) 
            case 36:
                return Token(pos, TokenName.SETA) 
            case 37:
                return Token(pos, TokenName.SUB) 
            case 38:
                return Token(pos, TokenName.PONTO_VIRGULA) 
            case 39:
                return Token(pos, TokenName.VIRGULA) 
            case 40:
                return Token(pos, TokenName.ADD) 
            case 41:
                return Token(pos, TokenName.MUL) 
            case 42:
                return Token(pos, TokenName.POW) 
            case 100:
                return Token(pos, TokenName.EOF) 
            case _:
                raise Exception(f"Ação não definida para estado {s}")
    

class BufReader:
    def __init__(self, file_path, buffer_size=4096):
        self.file = open(file_path, "r", encoding="utf-8")
        self.buf_size = buffer_size
        self.buffer = ""
        self.buf_pos = 0
        self._fill_buffer()

    def _fill_buffer(self):
        buf = self.file.read(self.buf_size)
        if not buf:
            self.buffer = None
            return
        if len(self.buffer) == 0:
            self.buffer = buf
        else:
            self.buffer = self.buffer[self.buf_size:] + buf
            self.buf_pos = 0
    
    def read_char(self):
        if self.buffer is None:
            return None
        if self.buf_pos >= len(self.buffer):
            self._fill_buffer()
        if self.buffer is None or self.buf_pos >= len(self.buffer):
            return None
        c = self.buffer[self.buf_pos]
        self.buf_pos += 1
        return c
    
    def peek(self):
        if self.buffer is None or self.buf_pos >= len(self.buffer):
            return None
        return self.buffer[self.buf_pos]

    def go_back(self, n=1):
        if self.buf_pos - n < 0:
            raise IndexError("Cannot go back")
        self.buf_pos -= n

    def close(self):
        self.file.close()
