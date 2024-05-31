# Proof Of Concept
# Takes in a json object and dumps type information to a file
# Checks basic type safety
import argparse
import json

from graph import Graph, Node
from kvstore import KVStore, StoreValue
from sutypes import SuTypes, TypeRepr
from type_parser import get_test_custom_type_bindings, get_test_custom_type_values, get_test_parameter_type_values
from utils import DebugInfo


def load_data_body() -> dict:

    with open('ast.json') as data_file:
        data = json.load(data_file)

    return data['Methods']

def load_data_attributes() -> dict:

    with open('ast.json') as data_file:
        data = json.load(data_file)

    return data['Attributes']


def constraint_type_with_operator_value(value, type) -> bool:
    valid_constraints = {
        "Add": ["Number"],
    }

    if type == "Operator":
        return True

    if type == "Variable":
        return True

    valid_types = valid_constraints.get(value, None)
    if valid_types is None:
        raise NotImplementedError("constraint and operator not implemented")
    return type in valid_types

def get_valid_type_for_operator(value) -> TypeRepr:
    valid_types = {
        "Add": SuTypes.Number,
        "PostInc": SuTypes.Number,
        "Sub": SuTypes.Number,
        "Mul": SuTypes.Number,
        "And": SuTypes.Boolean,
        "Cat": SuTypes.String,
    }

    if (x:= valid_types.get(value, None)) is None:
        raise NotImplementedError("valid operator type not implemented")
    return TypeRepr({ "form": "Primitive", "meaning": [x], "name": SuTypes.to_str(x) })

def get_type_assertion_functions() -> list[str]:
    return [
        "String?",
        "Number?",
        "Boolean?",
        "Object?",
        "Class?",
        "Function?",
        "Date?",
    ]


def infer_generic(stmt, store, graph, attributes) -> TypeRepr:
    match stmt["Tag"]:
        case "Unary":
            return infer_unary(stmt, store, graph, attributes)
        case "Binary":
            return infer_binary(stmt, store, graph, attributes)
        case "Nary":
            return infer_nary(stmt, store, graph, attributes)
        case "Identifier":
            if store.get(stmt["ID"]) is not None:
                return store.get(stmt["ID"]).inferred
            return TypeRepr(TypeRepr.construct_definition_from_primitive(SuTypes.Any))
        case "If":
            return infer_if(stmt, store, graph, attributes)
        case "Compound":
            # ! possible useless expression error?
            if len(stmt["Args"]) == 0:
                return None
            return infer_generic(stmt["Args"][0], store, graph, attributes)
        case "Call":
            if store.get(stmt["Args"][0]["ID"]) is not None:
                if store.get(stmt["Args"][0]["ID"]).inferred != TypeRepr(TypeRepr.construct_definition_from_primitive(SuTypes.Function)):
                    raise TypeError(f"{store.get(stmt['Args'][0]['ID']).value} is not callable, it is of type {store.get(stmt['Args'][0]['ID']).inferred} instead")
            return infer_generic(stmt["Args"][0], store, graph, attributes)
        case "Return":
            return infer_generic(stmt["Args"][0], store, graph, attributes)
        case "Object":
            return infer_object(stmt["Args"], store, graph, attributes)
        case "Member":
            return infer_attribute(stmt, store, graph, attributes)
        case "Constant":
            return TypeRepr(TypeRepr.construct_definition_from_primitive(SuTypes.from_str(stmt["Type_t"])))
        case _:
            raise NotImplementedError(f"missed case {stmt['Tag']}")

def infer_unary(stmt, store, graph, attributes) -> TypeRepr:
    args = stmt["Args"]
    value = stmt["Value"]

    if value in ["LParen", "RParen"]:
        ret_t = infer_generic(args[0], store, graph, attributes)
        v = StoreValue(args[0]["Value"], 
                       TypeRepr(TypeRepr.construct_definition_from_primitive(SuTypes.from_str(args[0]["Type_t"]))),
                       ret_t)
        store.set(args[0]["ID"], v)
        return ret_t
     

    node = Node(args[0]["ID"])
    graph.add_node(node)

    valid_t = get_valid_type_for_operator(value)
    vn = Node(valid_t.name)
    graph.add_node(vn)
    graph.add_edge(node.value, vn.value)

    return valid_t


def infer_binary(stmt, store, graph, attributes) -> TypeRepr:
    args = stmt["Args"]
    lhs = args[0]
    rhs = args[1::][0]

    # inferred types of lhs and rhs should be the same
    lhs_t = infer_generic(lhs, store, graph, attributes)
    if lhs_t is not None and lhs["Type_t"] != "Operator":
        v = StoreValue(
            lhs["Value"], 
            TypeRepr(TypeRepr.construct_definition_from_primitive(SuTypes.from_str(lhs["Type_t"]))),
            lhs_t
        )
        store.set(lhs["ID"], v)
    rhs_t = infer_generic(rhs, store, graph, attributes)
    if rhs_t is not None and rhs["Type_t"] != "Operator":
        v = StoreValue(
            rhs["Value"], 
            TypeRepr(TypeRepr.construct_definition_from_primitive(SuTypes.from_str(rhs["Type_t"]))),
            rhs_t)
        store.set(rhs["ID"], v)

    # if not check_type_equivalence(lhs_t, rhs_t):
    #     raise TypeError(f"Type mismatch for {lhs_t} and {rhs_t}")
    lhs_n = Node(lhs["ID"])
    rhs_n = Node(rhs["ID"])
    graph.add_node(lhs_n)
    graph.add_node(rhs_n)
    graph.add_edge(lhs_n.value, rhs_n.value)

    if lhs_t != rhs_t:
        raise TypeError(f"Conflicting inferred types for variable {lhs['ID']}\nexisting: {lhs_t}, \ngot: {rhs_t}")
    elif lhs_t == TypeRepr(TypeRepr.construct_definition_from_primitive(SuTypes.Any)):
        store.set(lhs["ID"], StoreValue(rhs["Value"], 
            TypeRepr(TypeRepr.construct_definition_from_primitive(SuTypes.from_str(rhs["Type_t"]))),
            rhs_t
            )
        )
        return rhs_t
    elif rhs_t == TypeRepr(TypeRepr.construct_definition_from_primitive(SuTypes.Any)):
        store.set(rhs["ID"], StoreValue(lhs["Value"], 
                TypeRepr(TypeRepr.construct_definition_from_primitive(SuTypes.from_str(lhs["Type_t"]))),
                lhs_t
            )
        )
        return lhs_t

    return None


def infer_nary(stmt, store, graph, attributes) -> TypeRepr:
    value = stmt["Value"]
    args = stmt["Args"]

    valid_t = get_valid_type_for_operator(value)

    prev = None
    for i in args:
        if i["Tag"] == "Call":
            i = i["Args"][0]
            if i["Value"] in get_type_assertion_functions():
                typed_check_t = SuTypes.from_str(i["Value"].removesuffix("?"))
                typed_check_t = TypeRepr(TypeRepr.construct_definition_from_primitive(typed_check_t))
                type_checked_var = i["Args"][0]

                v = StoreValue(
                    type_checked_var["Value"], 
                    TypeRepr(TypeRepr.construct_definition_from_primitive(SuTypes.from_str(type_checked_var["Type_t"]))),
                    typed_check_t 
                    )
                store.set(type_checked_var["ID"], v)

                n = Node(type_checked_var["ID"])
                graph.add_node(n)
                primitive_type_node = graph.find_node(typed_check_t.get_name())
                graph.add_edge(n.value, primitive_type_node.value)

        n = Node(i["ID"])
        """
        NOTE: Infer Generic cause Args might not always be constants and variables,
                so infer a generic somewhere here to infer further
        """
        n_infer = infer_generic(i, store, graph, attributes)
        # v = StoreValue(i["Value"], TypeRepr(TypeRepr.construct_definition_from_primitive(SuTypes.from_str(i["Type_t"]))), valid_t)
        v = StoreValue(i["Value"], n_infer, valid_t)
        store.set(i["ID"], v)
        graph.add_node(n)
        if prev is not None:
            graph.add_edge(prev.value, n.value)
        prev = n

    valid_str = valid_t.get_name()
    n = graph.find_node(valid_str)
    # n.add_edge(prev)
    graph.add_edge(prev.value, n.value)

    return valid_t

def infer_if(stmt, store, graph, attributes):
    cond = stmt["Args"][0]
    cond_t = infer_generic(cond, store, graph, attributes)
    if cond_t is not None:
        v = StoreValue(
            cond["Value"], 
            TypeRepr(TypeRepr.construct_definition_from_primitive(SuTypes.from_str(cond["Type_t"]))),
            cond_t)
        store.set(cond["ID"], v)

    then = stmt["Args"][1]
    then_t = infer_generic(then, store, graph, attributes)
    if then_t is not None:
        v = StoreValue(
            then["Value"], 
            TypeRepr(TypeRepr.construct_definition_from_primitive(SuTypes.from_str(then["Type_t"]))), 
            then_t)
        store.set(then["ID"], v)

    if len(stmt["Args"]) == 3:
        else_t = infer_generic(stmt["Args"][2], store, graph, attributes)
        if else_t is not None:
            v = StoreValue(
                stmt["Args"][2]["Value"], 
                TypeRepr(TypeRepr.construct_definition_from_primitive(SuTypes.from_str(stmt["Args"][2]["Type_t"]))), 
                else_t)
            store.set(stmt["Args"][2]["ID"], v)

    return None

def infer_attribute(stmt, store, graph, attributes) -> TypeRepr:
    value = stmt["Value"]
    attrb_t = attributes.get(value, None)

    if attrb_t is None:
        raise TypeError(f"Attribute `{value}` not found in current class")
    
    valid_t = TypeRepr(TypeRepr.construct_definition_from_primitive(SuTypes.from_str(attrb_t["Type_t"])))
    v = StoreValue(stmt["Value"], 
                   TypeRepr(TypeRepr.construct_definition_from_primitive(SuTypes.from_str(stmt["Type_t"]))),
                   valid_t
                )
    store.set(stmt["ID"], v)

    n = Node(stmt["ID"])
    graph.add_node(n)
    t = graph.find_node(valid_t.get_name())
    # t.add_edge(n)
    graph.add_edge(n.value, t.value)

    return valid_t

def infer_object(stmt, store, graph, attributes):
    obj_def = {}

    for i in stmt:
        t = infer_generic(i["Args"][0], store, graph, attributes)
        v = StoreValue(i["Args"][0]["Value"], TypeRepr(TypeRepr.construct_definition_from_primitive(SuTypes.from_str(i["Args"][0]["Type_t"]))), t)
        store.set(i["Args"][0]["ID"], v)
        # construct obj def struct for TypeRepr
        obj_def[i["Value"]] = t
        n = Node(i["Args"][0]["ID"])
        graph.add_node(n)
        graph.add_edge(n.value, graph.find_node(t.get_name()).value)

    return TypeRepr({"form": "Object", "meaning": obj_def})

def propogate_infer(store, graph, typedefs, attributes, check=False):
    primitives = graph.get_basal_types()

    # dfs through each primitive and assign the same sutype to connecting nodes
    for x, p in enumerate(primitives):
        if x == 10:
            pass
        p = graph.find_node(p.value)
        
        type_value = None
        if p.value in graph.get_primitive_type_string():
            type_value = TypeRepr(TypeRepr.construct_definition_from_primitive(SuTypes.from_str(p.value)))
        elif typedefs.get(p.value) is not None:
            type_value = TypeRepr(typedefs[p.value])
        
        if type_value is None:
            raise ValueError(f"Type not found for {p.value}")

        p.propogate_type(store, new_type=type_value, check=check)

def parse_class(clss):
    members = {}

    for k, v in clss.items():
        members[k] = v[0]

    return members

def process_parameters(methods, typedefs, bindings, param_t, store, graph, attributes, dbg=None):
    for k, v in methods.items():
        if dbg is not None:
            dbg.set_func(k)
        if v["Parameters"] != []:
            if param_t.get(k) is None:
                continue
            if len(v["Parameters"]) != len(param_t.get(k)):
                raise ValueError(f"Parameter length mismatch for method {k}, function expects {len(v['Parameters'])} got {len(param_t.get(k))}")
            for p in v["Parameters"]:
                p_id = p["ID"]
                p_t = param_t.get(k).get(p["Value"])
                if p_t is not None:
                    tr = TypeRepr(p_t)
                    v = StoreValue(p_id, TypeRepr(p_t), TypeRepr(p_t))
                    store.set(p_id, v)
                    n = Node(p_id)
                    graph.add_node(n)

                    primitive_type_node = graph.find_node(tr.get_name())
                    if primitive_type_node is None:
                        # check for custom type or if aliased
                        var = k + '_' + p["Value"]
                        if (b := bindings.get(var, None)) is not None:
                            primitive_type_node = graph.find_node(b)

                    graph.add_edge(n.value, primitive_type_node.value)
            
def process_custom_types(methods, typedefs, bindings, param_t, store, graph, attributes, dbg=None):
    for fn, body in methods.items():
        if dbg is not None:
            dbg.set_func(fn)
        # get all keys and values in bindings that begin with k_
        b = {k: v for k, v in bindings.items() if k.startswith(f"{fn}_")}
        if b != {}:
            addedQ = False
            for var, var_t in b.items():
                for i in body["Body"]:
                    var = var.removeprefix(fn + "_")
                    id_found = lookup_variable(var, i[0])
                    if (id_found is not None) or ((not addedQ) and (var == list(param_t.get(fn).keys())[0])):
                        if id_found is None:
                            id_found = [x["ID"] for x in methods.get(fn).get("Parameters") if x["Value"] == var][0]

                        unknown_type = TypeRepr(TypeRepr.construct_definition_from_primitive(SuTypes.Unknown))
                        inf_t = TypeRepr(typedefs[var_t])
                        v = StoreValue(var, unknown_type, inf_t)
                        store.set(id_found, v)

                        if graph.find_node(typedefs[var_t]) is None:
                            graph.add_basal_type(Node(var_t))
                        
                        n = Node(id_found)
                        graph.add_node(n)

                        primitive_type_node = graph.find_node(var_t)
                        graph.add_edge(n.value, primitive_type_node.value)

                        addedQ = True

# like infer_generic, but no inference, just matches the string of the variable passed in and return the ID
def lookup_variable(var, stmt):
    match stmt["Tag"]:
        case "Unary":
            return lookup_variable(var, stmt["Args"][0])
        case "Binary":
            return lookup_variable(var, stmt["Args"][0]) or lookup_variable(var, stmt["Args"][1])
        case "Nary":
            return [lookup_variable(var, i) for i in stmt["Args"]]
        case "Identifier":
            if stmt["Value"] == var:
                return stmt["ID"]
            return None
        case "If":
            return lookup_variable(var, stmt["Args"][0]) or lookup_variable(var, stmt["Args"][1]) or lookup_variable(var, stmt["Args"][2])
        case "Call" | "Compound":
            return lookup_variable(var, stmt["Args"][0])
        case "Return":
            return lookup_variable(var, stmt["Args"][0])
        case "Object":
            return [lookup_variable(var, i) for i in stmt["Args"]]
        case "Member":
            return lookup_variable(var, stmt["Args"][0])
        case "Constant":
            return None
        case _:
            raise NotImplementedError(f"missed case {stmt['Tag']}")


def process_methods(methods, store, graph, attributes, dbg=None):
    for k, v in methods.items():
        if dbg is not None:
            dbg.set_func(k)
        if k == "GetUserAuthCall":
            pass
        for x, i in enumerate(v["Body"]):
            if dbg is not None:
                dbg.set_line(x + 1)
            valid_t = infer_generic(i[0], store, graph, attributes)
            if valid_t is None:
                continue
            v = StoreValue(
                i[0]["Value"], 
                TypeRepr(TypeRepr.construct_definition_from_primitive(SuTypes.from_str(i[0]["Type_t"]))), 
                valid_t
                )
            store.set(i[0]["ID"], v)
            n = Node(i[0]["ID"])
            graph.add_node(n)

            if graph.find_node(valid_t.get_name()) is None:
                graph.add_node(Node(valid_t.get_name()))

            graph.add_edge(n.value, graph.find_node(valid_t.get_name()).value)



def main():
    global debug_info
    debug_info = DebugInfo()

    p = argparse.ArgumentParser("Type Inference")
    p.add_argument("-t", action="store_true")
    args = p.parse_args()

    graph = Graph()
    store = KVStore()
    attributes = parse_class(load_data_attributes())
    methods = parse_class(load_data_body())

    # print("=" * 80)
    ascii_blocks = """
     ____  _     ___   ____ _  ______  
    | __ )| |   / _ \ / ___| |/ / ___| 
    |  _ \| |  | | | | |   | ' /\___ \ 
    | |_) | |__| |_| | |___| . \ ___) |
    |____/|_____\___/ \____|_|\_\____/ 
    """
    # print(ascii_blocks)
    # print("=" * 80)

    param_t = get_test_parameter_type_values()
    typedefs = get_test_custom_type_values()
    bindings = get_test_custom_type_bindings()

    # try:
    process_custom_types(methods, typedefs, bindings, param_t, store, graph, attributes, dbg=debug_info)
    process_parameters(methods, typedefs, bindings, param_t, store, graph, attributes, dbg=debug_info) 
    process_methods(methods, store, graph, attributes, dbg=debug_info)
    propogate_infer(store, graph, typedefs, attributes, check=False)
    # except Exception as e:
    #     if not args.t:
    #         print(f"Exception: {e}")
    #     else:
    #         debug_info.trigger(e)

    # graph.visualise()
    
    # print("=" * 80)
    ascii_store = """
     ____ _____ ___  ____  _____ 
    / ___|_   _/ _ \|  _ \| ____|
    \___ \ | || | | | |_) |  _|  
     ___) || || |_| |  _ <| |___ 
    |____/ |_| \___/|_| \_\_____|

    """
    # print(ascii_store)
    # print("=" * 80)
    # print(json.dumps(store.to_json(), indent=4))
    # print("=" * 80)
    ascii_graph = """
      ____ ____      _    ____  _   _ 
     / ___|  _ \    / \  |  _ \| | | |
    | |  _| |_) |  / _ \ | |_) | |_| |
    | |_| |  _ <  / ___ \|  __/|  _  |
     \____|_| \_\/_/   \_\_|   |_| |_|

    """
    # print(ascii_graph)
    # print("=" * 80)
    # print(json.dumps(graph.to_json(), indent=4))

    with open("type_store.json", "w") as fobj:
        json.dump(store.to_json(), fobj, indent=4)

    with open("type_graph.json", "w") as fobj:
        json.dump(graph.to_json(), fobj, indent=4)

if __name__ == "__main__":
    main()
