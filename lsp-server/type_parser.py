import json

from sutypes import SuTypesEncoder, SuTypes


class Parser:
    def __init__(self):
        self.typedef = {}

    def parse(self, typedef_string):
        lines = typedef_string.split('\n')
        for line in lines:
            line = line.strip()
            if line:
                self.parse_line(line)
        return self.typedef

    def parse_line(self, line):
        parts = line.split('>>=')
        self.typename = parts[0].strip().removeprefix('type').strip()
        definition = parts[1].strip()
        if '->' in definition:
            self.typedef[self.typename] = self.parse_function(definition)
        elif '|' in definition:
            self.typedef[self.typename] = self.parse_union(definition)
        elif '&' in definition:
            self.typedef[self.typename] = self.parse_intersection(definition)
        elif ':' in definition:
            self.typedef[self.typename] = self.parse_object(definition)
        else:
            self.typedef[self.typename] = definition.strip()

    def parse_function(self, definition):
        func_params, args_return = definition.split('->')
        func_params = func_params.strip().removeprefix('fn').removeprefix('(').removesuffix(')').strip()
        args_return = args_return.strip()
        args = [arg.strip() for arg in func_params.split(',') if arg.strip()]
        args_dict = {}
        for arg in args:
            arg_name, arg_type = arg.split(':')
            args_dict[arg_name.strip()] = self.resolve_type(arg_type.strip())
        return {"parameters": args_dict, "return": self.resolve_type(args_return)}

    def parse_union(self, definition):
        types = [self.resolve_type(t.strip()) for t in definition.split('|')]
        return {"union": types}

    def parse_intersection(self, definition):
        types = [self.resolve_type(t.strip()) for t in definition.split('&')]
        return {"intersection": types}

    def parse_object(self, definition):
        properties = {}
        props = [prop.strip() for prop in definition.split(',')]
        for prop in props:
            prop_name, prop_type = prop.split(':')
            properties[prop_name.strip()] = self.resolve_type(prop_type.strip())
        return properties

    def resolve_type(self, type_name):
        return SuTypes.from_str(type_name)

    def generate_json(self):
        return json.dumps(self.typedef, indent=4, cls=SuTypesEncoder)

def get_test_parameter_type_values():
    return {
        "originalTestFunc":  {"x": { "form": "Primitive", "name": "Number", "meaning": [SuTypes.Number] }, 
                              "y": { "form": "Primitive", "name": "Number", "meaning": [SuTypes.Number] },
                              "z": { "form": "Primitive", "name": "Number", "meaning": [SuTypes.Number] }},
        "SameVarID": {"x": { "form": "Primitive", "name": "Number", "meaning": [SuTypes.String]}},
        "ParameterMismatch": {"x": { "form": "Primitive", "name": "Number", "meaning": [SuTypes.Number]}},
        # "IncorrectNumberOfParamsTyped":  {"x": { "form": "Primitive", "name": "Number", "meaning": [SuTypes.Number] }, 
        #                       "z": { "form": "Primitive", "name": "Number", "meaning": [SuTypes.Number] }},
        "simpleTypeAlias": {"a": { "form": "Alias", "name": "Number2", "meaning": [SuTypes.Number] }},
        "GetUserAuth": {"usr": { "form": "Object", "meaning": {"name": SuTypes.String, "age": SuTypes.Number} }},
    }

def get_test_custom_type_bindings():
    return {
        "currencyTypeAlias_u": "Currency",
        "currencyTypeAlias_nu": "Currency",
        "currencyTypeAlias_ou": "Currency",
        "simpleTypeAlias_a": "Number2",
        "GetUserAuth_usr": "User",
    }

def get_test_custom_type_values():
    return {
        "Number2": {"form": "Primitive", "name": "Number", "meaning": [SuTypes.Number]},
        "Currency": {"form": "Union", "meaning": ["USD", "CAD", "GBP"]},
        "MyNumber": {"form": "Alias","meaning": [SuTypes.Number]},
        "User": {"form": "Object", "meaning": {"name": SuTypes.String, "age": SuTypes.Number}},
    }

if __name__ == "__main__":
    p = Parser()
    p.parse("type originalTestFunc >>= fn(x: String, y: Number, z: Number) -> Any")
    print(p.generate_json())

    p = Parser()    
    p.parse("type MyNumber >>= Number")
    print(p.generate_json())

    p = Parser()
    p.parse('type Currency >>= "USD" | "CAD" | "GBP"')
    print(p.generate_json())
