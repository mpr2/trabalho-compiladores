from Lexer import Lexer
from Token import TokenName

if __name__ == "__main__":
    lexer = Lexer("in.txt")
    try:
        t = lexer.next_token()
        while t.name != TokenName.EOF:
            print(t)
            t = lexer.next_token()
        print(t)
    except Exception as e:
        print(f"Erro na análise léxica: {e}")
