from Parser import Parser

if __name__ == "__main__":
    parser = Parser("in.txt")
    try:
        tree = parser.parse()
        tree.pretty_print()
    except Exception as e:
        print("Não foi possível processar o arquivo:")
        print(e)
