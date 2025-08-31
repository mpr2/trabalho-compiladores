from Lexer import Lexer
from Token import TokenName
from Tree import Tree

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
        tree = Tree('PROGRAMA')

        self._check_token(TokenName.MAIN, tree)
        self._check_token(TokenName.ID, tree)
        self._check_token(TokenName.PAR_ESQ, tree)
        self._check_token(TokenName.PAR_DIR, tree)

        tree.add_child(self._parse_bloco())

        self.token = self.lexer.next_token()
        if self.token.name != TokenName.EOF:
            raise Exception(f"{self.token.pos} Erro sintático: fim de arquivo esperado")
        return tree
    
    def _parse_bloco(self):
        tree = Tree('BLOCO')
        self._check_token(TokenName.INICIO, tree)
        tree.add_child(self._parse_declaracoes())
        tree.add_child(self._parse_comandos())
        self._check_token(TokenName.FIM, tree)
        return tree
    
    def _parse_declaracoes(self):
        tree = Tree('DECLARACOES')
        while (token := self.lexer.peek_token()) and token.name in self.first['declaracao']:
            self.token = self.lexer.next_token()
            self.id_was_read = True
            peek = self.lexer.peek_token()
            if peek.name == TokenName.SETA or peek.name == TokenName.VIRGULA:
                tree.add_child(self._parse_declaracao())
            else:
                break
        if not tree.is_leaf():
            return tree
        return None

    def _parse_declaracao(self):
        tree = Tree('DECLARACAO')
        tree.add_child(self._parse_lista_ids())
        self._check_token(TokenName.SETA, tree)
        self._check_token(TokenName.TIPO, tree)
        self._check_token(TokenName.PONTO_VIRGULA, tree)
        return tree

    def _parse_lista_ids(self):
        tree = Tree('LISTA_IDS')
        if self.id_was_read:
            self.id_was_read = False
            tree.add_child(Tree(self.token))
        else:
            self._check_token(TokenName.ID, tree)
        tree.add_child(self._parse_lista_ids2())
        return tree
    
    def _parse_lista_ids2(self):
        tree = Tree('LISTA_IDS2')
        token = self.lexer.peek_token()
        if token.name == TokenName.VIRGULA:
            self.token = self.lexer.next_token()
            tree.add_child(Tree(self.token))
            tree.add_child(self._parse_lista_ids())
            return tree
        return None

    def _parse_comandos(self):
        tree = Tree('COMANDOS')
        while self.id_was_read or ((token := self.lexer.peek_token()) and token.name in self.first['comando']):
            tree.add_child(self._parse_comando())
        if not tree.is_leaf():
            return tree
        return None

    def _parse_comando(self):
        tree = Tree('COMANDO')
        token = self.lexer.peek_token()
        if token.name in self.first['selecao']:
            tree.add_child(self._parse_selecao())
        elif token.name in self.first['repeticao']:
            tree.add_child(self._parse_repeticao())
        elif self.id_was_read or token.name in self.first['atribuicao']:
            tree.add_child(self._parse_atribuicao())
        else:
            self.token = self.lexer.next_token()
            self._erro(f"{self.first['selecao'].union(self.first['repeticao']).union(self.first['atribuicao'])}")
        return tree

    def _parse_selecao(self):
        tree = Tree('SELECAO')
        self._check_token(TokenName.CASO, tree)
        self._check_token(TokenName.PAR_ESQ, tree)
        tree.add_child(self._parse_condicao())
        self._check_token(TokenName.PAR_DIR, tree)
        self._check_token(TokenName.ENTAO, tree)
        tree.add_child(self._parse_cmd_bloco())
        tree.add_child(self._parse_senao())
        return tree

    def _parse_senao(self):
        tree = Tree('SENAO')
        token = self.lexer.peek_token()
        if token.name == TokenName.SENAO:
            self.token = self.lexer.next_token()
            tree.add_child(Tree(self.token))
            tree.add_child(self._parse_cmd_bloco())
        if not tree.is_leaf():
            return tree
        return None

    def _parse_condicao(self):
        tree = Tree('CONDICAO')
        tree.add_child(self._parse_expressao())
        self._check_token(TokenName.RELOP, tree)
        tree.add_child(self._parse_expressao())
        return tree

    def _parse_cmd_bloco(self):
        tree = Tree('CMD_BLOCO')
        token = self.lexer.peek_token()
        if token.name in self.first['comando']:
            tree.add_child(self._parse_comando())
        elif token.name in self.first['bloco']:
            tree.add_child(self._parse_bloco())
        else:
            self.token = self.lexer.next_token()
            self._erro(f"{self.first['comando'].union(self.first['bloco'])}")
        return tree

    def _parse_repeticao(self):
        tree = Tree('REPETICAO')
        token = self.lexer.peek_token()
        if token.name in self.first['enquanto']:
            tree.add_child(self._parse_enquanto())
        elif token.name in self.first['ate']:
            tree.add_child(self._parse_ate())
        else:
            self.token = self.lexer.next_token()
            self._erro(f"{self.first['enquanto'].union(self.first['ate'])}")
        return tree

    def _parse_enquanto(self):
        tree = Tree('ENQUANTO')
        self._check_token(TokenName.ENQUANTO, tree)
        self._check_token(TokenName.PAR_ESQ, tree)
        tree.add_child(self._parse_condicao())
        self._check_token(TokenName.PAR_DIR, tree)
        self._check_token(TokenName.FACA, tree)
        tree.add_child(self._parse_cmd_bloco())
        return tree

    def _parse_ate(self):
        tree = Tree('ATE')
        self._check_token(TokenName.REPITA, tree)
        tree.add_child(self._parse_cmd_bloco())
        self._check_token(TokenName.ATE, tree)
        self._check_token(TokenName.PAR_ESQ, tree)
        tree.add_child(self._parse_condicao())
        self._check_token(TokenName.PAR_DIR, tree)
        self._check_token(TokenName.PONTO_VIRGULA, tree)
        return tree

    def _parse_atribuicao(self):
        tree = Tree('ATRIBUICAO')
        if self.id_was_read:
            self.id_was_read = False
            tree.add_child(Tree(self.token))
        else:
            self._check_token(TokenName.ID, tree)
        self._check_token(TokenName.ATRIB, tree)
        tree.add_child(self._parse_expressao())
        self._check_token(TokenName.PONTO_VIRGULA, tree)
        return tree

    def _parse_expressao(self):
        tree = Tree('EXPRESSAO')
        tree.add_child(self._parse_termo())
        tree.add_child(self._parse_expressao2())
        return tree

    def _parse_expressao2(self):
        tree = Tree('EXPRESSAO2')
        while True:
            token = self.lexer.peek_token()
            if token.name == TokenName.ADD or token.name == TokenName.SUB:
                self.token = self.lexer.next_token()
                tree.add_child(Tree(self.token))
                tree.add_child(self._parse_termo())
            else:
                break
        if not tree.is_leaf():
            return tree
        return None

    def _parse_termo(self):
        tree = Tree('TERMO')
        tree.add_child(self._parse_fator())
        tree.add_child(self._parse_termo2())
        return tree

    def _parse_termo2(self):
        tree = Tree('TERMO2')
        while True:
            token = self.lexer.peek_token()
            if token.name == TokenName.MUL or token.name == TokenName.DIV:
                self.token = self.lexer.next_token()
                tree.add_child(Tree(self.token))
                tree.add_child(self._parse_fator())
            else:
                break
        if not tree.is_leaf():
            return tree
        return None

    def _parse_fator(self):
        tree = Tree('FATOR')
        tree.add_child(self._parse_atomo())
        tree.add_child(self._parse_fator2())
        return tree

    def _parse_fator2(self):
        tree = Tree('FATOR2')
        token = self.lexer.peek_token()
        if token.name == TokenName.POW:
            self.token = self.lexer.next_token()
            tree.add_child(Tree(self.token))
            tree.add_child(self._parse_fator())
            return tree
        return None

    def _parse_atomo(self):
        tree = Tree('ATOMO')
        while (token := self.lexer.peek_token()) and token.name == TokenName.SUB:
            self.token = self.lexer.next_token()
            tree.add_child(Tree(self.token))
        self.token = self.lexer.next_token()
        if self.token.name in {TokenName.ID, TokenName.CONST_NUM, TokenName.CONST_CHAR}:
            tree.add_child(Tree(self.token))
        elif self.token.name == TokenName.PAR_ESQ:
            tree.add_child(Tree(self.token))
            tree.add_child(self._parse_expressao())
            self._check_token(TokenName.PAR_DIR, tree)
        else:
            self._erro({TokenName.SUB, TokenName.ID, TokenName.CONST_NUM, TokenName.CONST_CHAR, TokenName.PAR_ESQ})
        return tree

    def _check_token(self, token_name, tree):
        self.token = self.lexer.next_token()
        if self.token.name != token_name:
            self._erro(token_name)
        tree.add_child(Tree(self.token))
        
    def _erro(self, expected):
        raise Exception(f'{self.token.pos} Erro sintático: {expected} esperado, {self.token.name} encontrado.')

    def get_symbol_table(self):
        return self.lexer.symbol_table
