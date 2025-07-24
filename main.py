from Lexer import Lexer

if __name__ == "__main__":
    lexer = Lexer("in.txt")
    while (t := lexer.next_token()) != "EOF":
        print(t)
    