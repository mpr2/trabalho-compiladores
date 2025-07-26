from Token import Token, TokenName, TokenAttr

class Lexer:
    def __init__(self, file_path):
        self.reader = BufReader(file_path)
        self.pos = (1,1)
        self.table = TransitionTable(self.reader)
        self.lexeme_buffer = ""  

    def next_token(self):
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
            count['chars'] += 1
            if c == '\n':
                count['lf'] += 1
                count['last_lf'] = count['chars']
                
        x = self.table.actions(s, self.pos, count, self.lexeme_buffer)
        self.pos = (
            self.pos[0] + count['lf'],
            self.pos[1] + count['chars'] if count['lf'] == 0 else count['chars'] - count['last_lf'] + 1
        )
        if x.name == TokenName.IGNORE:
            return self.next_token()
        return x


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
                '-': 35,  # Subtração/seta
                None: 11  # EOF
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

    def initial(self):
        return 0

    def final(self, s):
        return s in [-1, 2, 6, 7, 9, 16, 17, 20, 23, 24, 26, 28, 29, 31, 32, 33, 34, 36, 37, 38, 39, 40, 41, 11]

    def move(self, s, c):
        if s not in self.table:
            raise Exception(f"Estado inválido: {s}")
        
        state_transitions = self.table[s]
        if state_transitions is None:
            raise Exception("Transição inválida: estado final")
        
        # Verifica transição específica
        if c in state_transitions:
            return state_transitions[c]
        
        # Verifica transições genéricas
        if s == 18 and c != '\'' and c != '\\' and c is not None:
            return 19  
        
        # Verifica others
        if s in self.others:
            return self.others[s]
        
        # Caractere não esperado
        return -1
        
    def actions(self, s, pos, count, lexeme):
        if s == -1:
            raise Exception("Erro léxico")
        
        # Mapeamento de estados para tokens
        token_map = {
            2: Token(pos, TokenName.IGNORE),
            6: Token(pos, TokenName.IGNORE),
            7: Token(pos, TokenName.DIV),
            9: self._handle_id_or_keyword(pos, lexeme),
            11: Token(pos, TokenName.EOF),
            16: Token(pos, TokenName.CONST_NUM, lexeme),
            17: Token(pos, TokenName.CONST_NUM, lexeme),
            20: Token(pos, TokenName.CONST_CHAR, lexeme[1:-1]),
            23: Token(pos, TokenName.RELOP, TokenAttr.EQ),
            24: Token(pos, TokenName.ATRIB),
            26: Token(pos, TokenName.RELOP, TokenAttr.NE),
            28: Token(pos, TokenName.RELOP, TokenAttr.LE),
            29: Token(pos, TokenName.RELOP, TokenAttr.LT),
            31: Token(pos, TokenName.RELOP, TokenAttr.GE),
            32: Token(pos, TokenName.RELOP, TokenAttr.GT),
            33: Token(pos, TokenName.PAR_ESQ),
            34: Token(pos, TokenName.PAR_DIR),
            36: Token(pos, TokenName.SETA),
            37: Token(pos, TokenName.SUB),
            38: Token(pos, TokenName.PONTO_VIRGULA),
            39: Token(pos, TokenName.VIRGULA),
            40: Token(pos, TokenName.ADD),
            41: Token(pos, TokenName.MUL),
        }
        
        # Estados que precisam retroceder
        if s in [2, 7, 9, 16, 17, 24, 29, 32, 37]:
            self._go_back(count)
            lexeme = lexeme[:-1]  # Remove último caractere (não pertence ao token)
        
        if s in token_map:
            return token_map[s]
        
        raise Exception(f"Ação não definida para estado {s}")
    
    def _handle_id_or_keyword(self, pos, lexeme):
        # Remove último caractere (não pertence ao token)
        clean_lexeme = lexeme[:-1]
        
        # Palavras-chave
        keywords = {
            "main": TokenName.MAIN,
            "inicio": TokenName.INICIO,
            "fim": TokenName.FIM,
            "caso": TokenName.CASO,
            "entao": TokenName.ENTAO,
            "senao": TokenName.SENAO,
            "enquanto": TokenName.ENQUANTO,
            "faca": TokenName.FACA,
            "repita": TokenName.REPITA,
            "ate": TokenName.ATE,
            "int": TokenName.TIPO,
            "char": TokenName.TIPO,
            "float": TokenName.TIPO,
        }
        
        if clean_lexeme.lower() in keywords:
            return Token(pos, keywords[clean_lexeme.lower()])
        return Token(pos, TokenName.ID, clean_lexeme)

    def _go_back(self, count):
        self.reader.go_back()
        count['chars'] -= 1
        if self.reader.peek() == '\n':
            count['lf'] = 0
            count['last_lf'] = -1


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
