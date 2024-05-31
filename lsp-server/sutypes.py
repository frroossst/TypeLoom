from enum import Enum
import json
import uuid


class SuTypes(Enum):
    Unknown = 0
    String = 1
    Number = 2
    Boolean = 3
    Any = 4
    NotApplicable = 5
    Never = 6
    Function = 7
    Object = 8
    Date = 9
    InBuiltOperator = 10
    Union = 11
    Intersect = 12

    @staticmethod
    def from_str(str):
        if isinstance(str, SuTypes):
            return str

        match str:
            case "String":
                return SuTypes.String
            case "Number":
                return SuTypes.Number
            case "Unknown":
                return SuTypes.Unknown
            case "Boolean":
                return SuTypes.Boolean
            case "Member":
                return SuTypes.Unknown
            case "Any" | "Variable":
                return SuTypes.Any
            case "Object":
                return SuTypes.Object
            case "Date":
                return SuTypes.Date
            case "Return":
                return SuTypes.Unknown
            case "Operator" | "PostInc" | "Callable" | "Compound" | "If" | "InBuiltOperator":
                return SuTypes.InBuiltOperator
            case "Union":
                return SuTypes.Union
            case "Intersect":
                return SuTypes.Intersect
            case "NotApplicable":
                return SuTypes.NotApplicable
            case "Never":
                return SuTypes.Never
            case "Function":
                return SuTypes.Function
            case _:
                raise ValueError(f"Unknown type {str} converting to SuTypes enum")

    @staticmethod
    def to_str(t):
        match t:
            case SuTypes.String:
                return "String"
            case SuTypes.Number:
                return "Number"
            case SuTypes.Unknown:
                return "Variable"
            case SuTypes.InBuiltOperator:
                return "Operator"
            case SuTypes.Boolean:
                return "Boolean"
            case SuTypes.Any:
                return "Any"
            case SuTypes.Date:
                return "Date"
            case SuTypes.Union:
                return "Union"
            case SuTypes.Intersect:
                return "Intersect"
            case _:
                raise ValueError(f"Unknown type {t} converting to string")

    @staticmethod
    def get_member_string():
        return ["Unknown", "String", "Number", "Boolean", "Any", "NotApplicable", "Never", "Function", "Object", "Date", "InBuiltOperator", "Union", "Intersect"]


class SuTypesEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Enum):
            return obj.name
        return json.JSONEncoder.default(self, obj)


class TypeRepr:

    name = None

    solved_t = None

    definition = None
    """
    definition is a dictionary of the form:
    {
        "form": "Primitive",
        "name": "Number",
        "meaning": [SuTypes.Number]
    }

    {
        "form": "Union",
        "name": "StrNum",
        "meaning": [SuTypes.String, SuTypes.Number]
    }

    {
        "form": "Alias",
        "name": "MyType",
        "meaning": [SuTypes.Boolean]
    }

    {
        "form": "Object",
        "name": "User",
        "meaning": {
            "name": SuTypes.String,
            "age": SuTypes.Number
        }
    }

    """

    def __init__(self, definition):
        if not isinstance(definition, dict):
            raise ValueError(f"definition should be a dictionary, got {definition}")
        if definition.get("form") is None or definition.get("meaning") is None:
            raise ValueError(f"definition should have form, meaning, got {definition}")

        if (name:= definition.get("name")) is None:
            self.name = str(uuid.uuid1()).replace("-", "")
        else:
            self.name = name

        for i in definition["meaning"]:
            if isinstance(i, str) and i in SuTypes.get_member_string():
                definition["meaning"] = [SuTypes.from_str(i)]

        self.literals = None
        if definition.get("value") is not None:
            self.literals = definition["value"]

        self.definition = definition
        self.solve_definition()

    def __repr__(self):
        return f"TypeRepr(name={self.name}, meaning={self.definition})"

    def __str__(self):
        return f"TypeRepr(name={self.name}, meaning={self.definition})"

    def is_(self, other):
        """
        a is b, when a or b is Any, Unknown will return False
        NOTE: a is_ b, is stricter than a == b
        """
        if not isinstance(other, TypeRepr):
            raise ValueError(f"Cannot compare SuTypes with {other}")

        self.solve_definition()
        other.solve_definition()

        # ? can there be a case where the types are unequal but the definitions are the same or vice-versa?
        return set(self.definition.get("meaning", None)) == set(other.definition.get("meaning", None))

    def is_not(self, other):
        return not self.is_(other)

    def __eq__(self, other):
        """
        a == b, when a or b is Any, Unknown will return True
        For more strict comparison use is_
        """
        # ANY CATCH
        s = self.definition.get("meaning", None)
        o = other.definition.get("meaning", None)
        if (s is None or o is None) or (len(s) == 1 or len(o) == 1):
            if set(s) <= set([SuTypes.Any, SuTypes.Unknown]) or set(o) <= set([SuTypes.Any, SuTypes.Unknown]):
                return True

        # OBJECT
        if self.definition["form"] == "Object":
            # check if all keys of self are in other and vice-versa
            if not all(k in other.definition["meaning"] for k in self.definition["meaning"]):
                return False

        # UNION
        if self.definition["form"] == "Union":
            return self.in_union(other)

        # PRIMITIVE
        if not isinstance(other, TypeRepr):
            raise ValueError(f"Cannot compare SuTypes with {other}")

        # ? can there be a case where the types are unequal but the definitions are the same or vice-versa?
        return set(self.definition.get("meaning", None)) == set(other.definition.get("meaning", None))

    def __ne__(self, __value: object) -> bool:
        return not self.__eq__(__value)

    def __lt__(self, other):
        if not isinstance(other, TypeRepr):
            raise ValueError(f"Cannot compare SuTypes with {other}")
        
        # ANY CATCH
        s = self.definition.get("meaning")
        o = other.definition.get("meaning")
        if len(s) == 1 or len(o) == 1:
            if set(s) <= set([SuTypes.Any, SuTypes.Unknown]) or set(o) <= set([SuTypes.Any, SuTypes.Unknown]):
                return True

        # OBJECT
        if self.definition["form"] == "Object":
            # check if self keys are a subset of other
            if not all(k in other.definition["meaning"] for k in self.definition["meaning"]):
                return False

        return set(self.definition.get("meaning", None)) < set(other.definition.get("meaning", None))

    def __le__(self, other):
        if not isinstance(other, TypeRepr):
            raise ValueError(f"Cannot compare SuTypes with {other}")

        return (self == other) or (self < other)

    def get_name(self):
        return self.name

    def get_equivalent_primitive_type(self):
        return self.solved_t

    def is_literal(self):
        return self.literals is not None

    def to_json(self):
        return json.dumps(self, cls=TypeReprEncoder)
    
    @classmethod
    def from_json(self, json_str):
        temp =  json.loads(json_str)
        temp_def = json.loads(temp["definition"])
        return temp_def

    def solve_definition(self):
        match self.definition["form"]:
            case "Union":
                return self.define_union()
            case "Intersect":
                return self.define_intersect()
            case "Alias":
                return self.define_alias()
            case "Function":
                return self.define_function()
            case "Object":
                return self.define_object()
            case "Primitive":
                return self.define_primitive()
            case _:
                raise ValueError(f"Unknown form {self.definition['form']}")

    def define_union(self):
        self.solved_t = []
        self.literals = []
        for i in self.definition["meaning"]:
            if isinstance(i, str):
                self.solved_t.append(SuTypes.String)
                self.literals.append(i)
            elif isinstance(i, int):
                self.solved_t.append(SuTypes.Number)
                self.literals.append(i)
            elif isinstance(i, bool):
                self.solved_t.append(SuTypes.Boolean)
                self.literals.append(i)
            elif isinstance(i, dict):
                self.solved_t.append(SuTypes.Object)
                self.literals.append(i)
            else:
                raise NotImplementedError(f"Union type {i} not implemented for solving")

        self.literals = list(set(self.literals))

    def in_union(self, literal):
        if (isinstance(literal, TypeRepr)):
            # check if literal has the member literal
            if literal.is_literal():
                return set(literal.literals) <= set(self.literals)

            if set(self.solved_t) <= set(literal.solved_t):
                return True
            else:
                return False

        if literal in self.literals:
            return True

        return False

    def define_alias(self):
        pass

    def define_object(self):
        struct = self.definition["meaning"]
        self.solved_t = struct

    def define_primitive(self):
        if len(self.definition["meaning"]) != 1:
            raise ValueError(f"Primitive type should have only one meaning, got {self.definition['meaning']}")
        self.solved_t = [SuTypes.from_str(self.definition["meaning"][0])]

    @staticmethod
    def construct_definition_from_primitive(t: SuTypes):
        return {
            "form": "Primitive",
            "name": t.name,
            "meaning": [t]
        }


class TypeReprEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, TypeRepr):
            return {
                "name": obj.name,
                "definition": json.dumps(obj.definition, cls=SuTypesEncoder)
            }
        return json.JSONEncoder.default(self, obj)




def check_type_equality(lhs, rhs) -> bool:
    if not (isinstance(lhs, SuTypes) and isinstance(rhs, SuTypes)):
        raise ValueError(f"lhs and rhs should be of type SuTypes, got {lhs} and {rhs}")

    if lhs == SuTypes.Any or rhs == SuTypes.Any:
        return True
    # does not matter if one of the types is an inbuilt operator
    if lhs == SuTypes.InBuiltOperator or rhs == SuTypes.InBuiltOperator:
        return True
    if lhs == SuTypes.Unknown or rhs == SuTypes.Unknown:
        # NOTE: Unknown is treated the same as Any; 
        # TODO: unknown would be removed as a type OR unknown checks would be enforced
        return True
    return lhs == rhs

def check_type_equal_or_subtype(parent, child):
    """
    @param parent: SuTypes
    @param child: SuTypes
    returns if the child is a subtype of the parent or is equal
    """
    if not (isinstance(parent, SuTypes) and isinstance(child, SuTypes)):
        raise ValueError(f"lhs and rhs should be of type SuTypes, got {parent} and {child}")

    are_equal = check_type_equality(parent, child)
    if are_equal:
        return True


if __name__ == "__main__":
    a = TypeRepr({"form": "Primitive", "name": "Number", "meaning": [SuTypes.Number]})
    b = TypeRepr({"form": "Primitive", "name": "Number", "meaning": [SuTypes.Number]})
    assert a == b

    a = TypeRepr({"form": "Union", "name": "Currency", "meaning": ["USD", "CAD", "GBP"]})
    b = TypeRepr({"form": "Union", "name": "Currency", "meaning": ["USD", "CAD", "GBP"]})
    assert a == b

    a = TypeRepr({"form": "Union", "name": "Currency", "meaning": ["USD", "CAD", "GBP"]})
    assert a.in_union("USD")

    a = TypeRepr({"form": "Object", "name": "User", "meaning": {"name": SuTypes.String, "age": SuTypes.Number}})
    b = TypeRepr({"form": "Object", "name": "User", "meaning": {"name": SuTypes.String, "age": SuTypes.Number}})
    assert a == b

    a = TypeRepr({"form": "Object", "name": "User", "meaning": {"name": SuTypes.String, "age": SuTypes.Number}})
    b = TypeRepr({"form": "Object", "name": "Admin", "meaning": {"name": SuTypes.String, "age": SuTypes.Number, "role": SuTypes.String}})
    assert a != b

    a = TypeRepr({"form": "Object", "name": "User", "meaning": {"name": SuTypes.String, "age": SuTypes.Number}})
    b = TypeRepr({"form": "Object", "name": "Admin", "meaning": {"name": SuTypes.String, "age": SuTypes.Number, "role": SuTypes.String}})
    assert a < b

    a = TypeRepr({"form": "Object", "name": "User", "meaning": {"name": SuTypes.String, "age": SuTypes.Number}})
    b = TypeRepr({"form": "Object", "name": "Admin", "meaning": {"name": SuTypes.String, "age": SuTypes.Number, "role": SuTypes.String}})
    assert not a > b

    a = TypeRepr({"form": "Union", "name": "Currency", "meaning": ["USD", "CAD", "GBP"]})
    b = TypeRepr({"form": "Primitive", "name": "Number", "meaning": [SuTypes.Number]})
    assert a != b

    a = TypeRepr({"form": "Union", "name": "Currency", "meaning": ["USD", "CAD", "GBP"]})
    b = TypeRepr({"form": "Primitive", "name": "String", "meaning": [SuTypes.String], "value": ["USD"]})
    assert a == b


