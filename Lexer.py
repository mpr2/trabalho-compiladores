from Token import Token, TokenName, TokenAttr

class Lexer:
    def __init__(self, file_path):
        self.reader = BufReader(file_path)
        self.pos = (1,1)
        self.table = TransitionTable(self.reader)

    def next_token(self):
        count = {
            'chars': 0,
            'lf': 0,
            'last_lf': -1,
        }
        s = self.table.initial()
        while not self.table.final(s):
            c = self.reader.read_char()
            s = self.table.move(s, c)
            count['chars'] += 1
            if c is '\n':
                count['lf'] += 1
                count['last_lf'] = count['chars']
        x = self.table.actions(s, self.pos, count)
        self.pos = (
            self.pos[0] + count['lf'],
            self.pos[1] + count['chars'] if count['lf'] is 0 else count['chars'] - count['last_lf'] + 1
        )
        if x.name is TokenName.IGNORE:
            return self.next_token()
        return x


class TransitionTable:
    def __init__(self, reader):
        self.reader = reader
        self.table = {
            -1: None,
            0: {
                '<': 1,
                '=': 5,
                '>': 6,
                ' ': 9,
                '\t': 9,
                '\n': 9,
                '\r': 9,
                None: 11,
            },
            1: {
                '=': 2,
                '>': 3,
            },
            2: None,
            3: None,
            4: None,
            5: None,
            6: {
                '=': 7,
            },
            7: None,
            8: None,
            9: {
                ' ': 9,
                '\t': 9,
                '\n': 9,
                '\r': 9,
            },
            10: None,
            11: None,
        }
        self.others = {
            0: -1,
            1: 4,
            6: 8,
            9: 10,
        }

    def initial(self):
        return 0

    def final(self, s):
        return self.table[s] is None

    def move(self, s, c):
        if s not in self.table:
            raise Exception("Estado inválido")
        if self.table[s] is None:
            raise Exception("Transição inválida: estado final")
        if c not in self.table[s]:
            return self.others[s]
        return self.table[s][c]
        
    def actions(self, s, pos, count):
        if s not in self.table:
            raise Exception("Estado inválido")
        if self.table[s] is not None:
            raise Exception("Sem ação prevista: estado não final")
        match s:
            case -1:
                raise Exception("Erro léxico")
            case 2:
                return Token(pos, TokenName.RELOP, TokenAttr.LE)
            case 3:
                return Token(pos, TokenName.RELOP, TokenAttr.NE)
            case 4:
                self._go_back(count)
                return Token(pos, TokenName.RELOP, TokenAttr.LT)
            case 5:
                return Token(pos, TokenName.RELOP, TokenAttr.EQ)
            case 7:
                return Token(pos, TokenName.RELOP, TokenAttr.GE)
            case 8:
                self._go_back(count)
                return Token(pos, TokenName.RELOP, TokenAttr.GT)
            case 10:
                self._go_back(count)
                return Token(pos, TokenName.IGNORE)
            case 11:
                return Token(pos, TokenName.EOF)
    
    def _go_back(self, count):
        self.reader.go_back()
        count['chars'] -= 1
        if self.reader.peek() is '\n':
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
            self.buffer = buf + self.file.read(self.buf_size)
        else:
            self.buffer = self.buffer[self.buf_size:] + buf
            self.buf_pos = self.buf_size
    
    def read_char(self):
        if not self.buffer:
            return None
        if self.buf_pos >= len(self.buffer):
            self._fill_buffer()
        if not self.buffer:
            return None
        c = self.buffer[self.buf_pos]
        self.buf_pos += 1
        return c
    
    def peek(self):
        if not self.buffer:
            return None
        return self.buffer[self.buf_pos]

    def go_back(self, n=1):
        if self.buf_pos-n < 0:
            raise IndexError
        self.buf_pos -= n

    def close(self):
        self.file.close()
