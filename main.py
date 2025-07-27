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

        print("\nTabela de símbolos: {")
        for lexeme in lexer.symbol_table:
            print(f"  {lexeme}: {lexer.symbol_table[lexeme]},")
        print("}\n")
    except Exception as e:
        print(f"Erro na análise léxica: {e}")
