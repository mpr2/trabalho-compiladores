from Lexer import Lexer
from Token import TokenName

if __name__ == "__main__":
    lexer = Lexer("in.txt")
    t = lexer.next_token()
    while t.name is not TokenName.EOF:
        print(t)
        t = lexer.next_token()
    print(t)
