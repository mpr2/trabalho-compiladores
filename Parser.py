from Lexer import Lexer
from Token import TokenName

class Parser:
    def __init__(self, file_path):
        self.lexer = Lexer(file_path)
        self.token = None
        self.id_was_read = False
        self.first = {
            'programa': {TokenName.MAIN},
            'bloco': {TokenName.INICIO},
            'declaracoes': {TokenName.ID},
            'declaracao': {TokenName.ID},
            'lista_ids': {TokenName.ID},
            'lista_ids2': {TokenName.VIRGULA},
            'comandos': {TokenName.CASO, TokenName.ENQUANTO, TokenName.REPITA, TokenName.ID},
            'comando': {TokenName.CASO, TokenName.ENQUANTO, TokenName.REPITA, TokenName.ID},
            'selecao': {TokenName.CASO},
            'senao': {TokenName.SENAO},
            'condicao': {TokenName.ID, TokenName.CONST_CHAR, TokenName.CONST_NUM, TokenName.SUB, TokenName.PAR_ESQ},
            'cmd_bloco': {TokenName.CASO, TokenName.ENQUANTO, TokenName.REPITA, TokenName.ID, TokenName.INICIO},
            'repeticao': {TokenName.ENQUANTO, TokenName.REPITA},
            'enquanto': {TokenName.ENQUANTO},
            'ate': {TokenName.REPITA},
            'atribuicao': {TokenName.ID},
            'expressao': {TokenName.ID, TokenName.CONST_NUM, TokenName.CONST_CHAR, TokenName.SUB, TokenName.PAR_ESQ},
            'expressao2': {TokenName.ADD, TokenName.SUB},
            'termo': {TokenName.ID, TokenName.CONST_NUM, TokenName.CONST_CHAR, TokenName.SUB, TokenName.PAR_ESQ},
            'termo2': {TokenName.MUL, TokenName.DIV},
            'fator': {TokenName.ID, TokenName.CONST_NUM, TokenName.CONST_CHAR, TokenName.SUB, TokenName.PAR_ESQ},
            'fator2': {TokenName.POW},
            'atomo': {TokenName.ID, TokenName.CONST_NUM, TokenName.CONST_CHAR, TokenName.SUB, TokenName.PAR_ESQ},
        }

    def parse(self):
        self._check_token(TokenName.MAIN)
        self._check_token(TokenName.ID)
        self._check_token(TokenName.PAR_ESQ)
        self._check_token(TokenName.PAR_DIR)
        self._parse_bloco()

        self.token = self.lexer.next_token()
        if self.token.name != TokenName.EOF:
            raise Exception("Erro sintático: fim de arquivo esperado")
        print("Sucesso")
    
    def _parse_bloco(self):
        self._check_token(TokenName.INICIO)
        self._parse_declaracoes()
        self._parse_comandos()
        self._check_token(TokenName.FIM)
    
    def _parse_declaracoes(self):
        while (token := self.lexer.peek_token()) and token.name in self.first['declaracao']:
            self.token = self.lexer.next_token()
            self.id_was_read = True
            peek = self.lexer.peek_token()
            if peek.name == TokenName.SETA or peek.name == TokenName.VIRGULA:
                self._parse_declaracao()
            else:
                break

    def _parse_declaracao(self):
        self._parse_lista_ids()
        self._check_token(TokenName.SETA)
        self._check_token(TokenName.TIPO)
        self._check_token(TokenName.PONTO_VIRGULA)

    def _parse_lista_ids(self):
        if self.id_was_read:
            self.id_was_read = False
        else:
            self._check_token(TokenName.ID)
        self._parse_lista_ids2()
    
    def _parse_lista_ids2(self):
        token = self.lexer.peek_token()
        if token.name == TokenName.VIRGULA:
            self.token = self.lexer.next_token()
            self._parse_lista_ids()

    def _parse_comandos(self):
        while self.id_was_read or ((token := self.lexer.peek_token()) and token.name in self.first['comando']):
            self._parse_comando()

    def _parse_comando(self):
        token = self.lexer.peek_token()
        if token.name in self.first['selecao']:
            self._parse_selecao()
        elif token.name in self.first['repeticao']:
            self._parse_repeticao()
        elif self.id_was_read or token.name in self.first['atribuicao']:
            self._parse_atribuicao()
        else:
            self.token = self.lexer.next_token()
            self._erro(f"{self.first['selecao'].union(self.first['repeticao']).union(self.first['atribuicao'])}")

    def _parse_selecao(self):
        self._check_token(TokenName.CASO)
        self._check_token(TokenName.PAR_ESQ)
        self._parse_condicao()
        self._check_token(TokenName.PAR_DIR)
        self._check_token(TokenName.ENTAO)
        self._parse_cmd_bloco()
        self._parse_senao()

    def _parse_senao(self):
        token = self.lexer.peek_token()
        if token.name == TokenName.SENAO:
            self.token = self.lexer.next_token()
            self._parse_cmd_bloco()

    def _parse_condicao(self):
        self._parse_expressao()
        self._check_token(TokenName.RELOP)
        self._parse_expressao()

    def _parse_cmd_bloco(self):
        token = self.lexer.peek_token()
        if token.name in self.first['comando']:
            self._parse_comando()
        elif token.name in self.first['bloco']:
            self._parse_bloco()
        else:
            self.token = self.lexer.next_token()
            self._erro(f"{self.first['comando'].union(self.first['bloco'])}")

    def _parse_repeticao(self):
        token = self.lexer.peek_token()
        if token.name in self.first['enquanto']:
            self._parse_enquanto()
        elif token.name in self.first['ate']:
            self._parse_ate()
        else:
            self.token = self.lexer.next_token()
            self._erro(f"{self.first['enquanto'].union(self.first['ate'])}")

    def _parse_enquanto(self):
        self._check_token(TokenName.ENQUANTO)
        self._check_token(TokenName.PAR_ESQ)
        self._parse_condicao()
        self._check_token(TokenName.PAR_DIR)
        self._check_token(TokenName.FACA)
        self._parse_cmd_bloco()

    def _parse_ate(self):
        self._check_token(TokenName.REPITA)
        self._parse_cmd_bloco()
        self._check_token(TokenName.ATE)
        self._check_token(TokenName.PAR_ESQ)
        self._parse_condicao()
        self._check_token(TokenName.PAR_DIR)
        self._check_token(TokenName.PONTO_VIRGULA)

    def _parse_atribuicao(self):
        if self.id_was_read:
            self.id_was_read = False
        else:
            self._check_token(TokenName.ID)
        self._check_token(TokenName.ATRIB)
        self._parse_expressao()
        self._check_token(TokenName.PONTO_VIRGULA)

    def _parse_expressao(self):
        self._parse_termo()
        self._parse_expressao2()

    def _parse_expressao2(self):
        while True:
            token = self.lexer.peek_token()
            if token.name == TokenName.ADD or token.name == TokenName.SUB:
                self.token = self.lexer.next_token()
                self._parse_termo()
            else:
                break

    def _parse_termo(self):
        self._parse_fator()
        self._parse_termo2()

    def _parse_termo2(self):
        while True:
            token = self.lexer.peek_token()
            if token.name == TokenName.MUL or token.name == TokenName.DIV:
                self.token = self.lexer.next_token()
                self._parse_termo()
            else:
                break

    def _parse_fator(self):
        self._parse_atomo()
        self._parse_fator2()

    def _parse_fator2(self):
        token = self.lexer.peek_token()
        if token.name == TokenName.POW:
            self.token = self.lexer.next_token()
            self._parse_fator()

    def _parse_atomo(self):
        while (token := self.lexer.peek_token()) and token.name == TokenName.SUB:
            self.token = self.lexer.next_token()
        self.token = self.lexer.next_token()
        if self.token.name in {TokenName.ID, TokenName.CONST_NUM, TokenName.CONST_CHAR}:
            pass
        elif self.token.name == TokenName.PAR_ESQ:
            self._parse_expressao()
            self._check_token(TokenName.PAR_DIR)
        else:
            self._erro({TokenName.SUB, TokenName.ID, TokenName.CONST_NUM, TokenName.CONST_CHAR, TokenName.PAR_ESQ})

    def _check_token(self, token_name):
        self.token = self.lexer.next_token()
        if self.token.name != token_name:
            self._erro(token_name)
        
    def _erro(self, expected):
        raise Exception(f'{self.token.pos} Erro sintático: {expected} esperado, {self.token.name} encontrado.')
