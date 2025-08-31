from Parser import Parser

if __name__ == "__main__":
    parser = Parser("in.txt")
    try:
        tree = parser.parse()
        tree.pretty_print()

        table = parser.get_symbol_table()
        print("\nTabela de símbolos: {")
        for lexeme in table:
            print(f"  {lexeme}: {table[lexeme]},")
        print("}")
    except Exception as e:
        print("Não foi possível processar o arquivo:")
        print(e)
