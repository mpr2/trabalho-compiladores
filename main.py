from Lexer import Lexer
from Parser import Parser
from Token import TokenName

if __name__ == "__main__":
    parser = Parser("in.txt")
    try:
        parser.parse()
    except Exception as e:
        print(e)
