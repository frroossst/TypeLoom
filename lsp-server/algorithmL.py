def add_custom_types_to_db():
    pass

def add_func_signatures_to_db():
    pass

def add_predefined_var_types_to_db():
    pass


def parser(ast):
    # consume the first line
    ast = "".join(ast.split("\n")[1:])

    return ast


def main():

    ast = parser(open("ast.loom").read())

    print(ast)

    add_custom_types_to_db()
    add_func_signatures_to_db()
    add_predefined_var_types_to_db()





if __name__ == "__main__":
    main()