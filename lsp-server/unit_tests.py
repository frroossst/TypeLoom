from graph import Graph
from kvstore import KVStore
from sutypes import SuTypes, TypeRepr
from type_inference import parse_class, process_parameters, process_methods, process_custom_types, propogate_infer


def should_fail(func):
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except TypeError:
            pass
        else:
            print(f"[FAILED] {func.__name__} should raise a TypeError")

    return wrapper

def should_pass(func):
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception:
            print(f"[FAILED] {func.__name__} should NOT raise a TypeError")
        else:
            pass

    return wrapper

def type_inference_test(methods, attributes, param_t, typedefs, bindings):
    graph = Graph()
    store = KVStore()

    process_parameters(methods, param_t, store, graph, attributes)
    process_custom_types(methods, typedefs, bindings, store, graph, attributes)
    process_methods(methods, store, graph, attributes)
    propogate_infer(store, graph, check=True)

"""
 _____         _       
|_   _|__  ___| |_ ___ 
  | |/ _ \/ __| __/ __|
  | |  __/\__ \ |_\__ \
  |_|\___||___/\__|___/
"""

@should_fail
def test_single_line_type_mismatch():
    _src = """
    class 
    	{
    	foo() 
    		{
    		x + "123"
    		}
    	}
    """
    ast = {
        "Tag": "Class",
        "Value": "nil",
        "Type_t": "Class",
        "Args": None,
        "Name": "",
        "Base": "class",
        "ID": "1f9d089323e0446ba607abd71291c4d5",
        "Methods": {
            "foo": [
                {
                    "Tag": "Function",
                    "Value": "",
                    "Type_t": "Function",
                    "Args": None,
                    "Name": "foo",
                    "ID": "bd1962804624407fb157795292e3c609",
                    "Parameters": [],
                    "Body": [
                        [
                            {
                                "Tag": "Nary",
                                "Value": "Add",
                                "Type_t": "Operator",
                                "Args": [
                                    {
                                        "Tag": "Identifier",
                                        "Value": "x",
                                        "Type_t": "Variable",
                                        "Args": None,
                                        "ID": "2931153bb41349c08bffbe72bba204e3"
                                    },
                                    {
                                        "Tag": "Constant",
                                        "Value": "\"123\"",
                                        "Type_t": "String",
                                        "Args": None,
                                        "ID": "41643df55d98458bbf2ec0c9a99ffc26"
                                    }
                                ],
                                "ID": "94ff1f1db7644c729132bde8458aefe1"
                            }
                        ]
                    ]
                }
            ]
        },
        "Attributes": {}
    }

    attributes = parse_class(ast["Attributes"])
    methods = parse_class(ast["Methods"])
    param_t, typedefs, bindings = {}, {}, {}

    type_inference_test(methods, attributes, param_t, typedefs, bindings)

@should_pass
def test_single_variable_reassignment_valid():
    _src = """
    class
        	{
        	foo()
                {
                x = 123
                x = 456
                }                
            """

    raise NotImplementedError()

@should_fail
def test_single_variable_reassignment():
    _src = """
    class 
    	{
    	foo() 
    		{
    		x = 123
    		x = "123"
    		}
    	}
    """
    ast = {
        "Tag": "Class",
        "Value": "nil",
        "Type_t": "Class",
        "Args": None,
        "Name": "",
        "Base": "class",
        "ID": "1f9d089323e0446ba607abd71291c4d5",
        "Methods": {
            "Reassignment": [
                {
                    "Tag": "Function",
                    "Value": "",
                    "Type_t": "Function",
                    "Args": None,
                    "Name": "Reassignment",
                    "ID": "adbb73e36cf2488cb665edc41a584d69",
                    "Parameters": [],
                    "Body": [
                        [
                            {
                                "Tag": "Binary",
                                "Value": "Eq",
                                "Type_t": "Operator",
                                "Args": [
                                    {
                                        "Tag": "Identifier",
                                        "Value": "x",
                                        "Type_t": "Variable",
                                        "Args": None,
                                        "ID": "5bdd9c52ce3547d0a7542fef3604d0e1"
                                    },
                                    {
                                        "Tag": "Constant",
                                        "Value": "123",
                                        "Type_t": "Number",
                                        "Args": None,
                                        "ID": "cd071ba4c1d24664b0067ac9037a7a33"
                                    }
                                ],
                                "ID": "a1860b50572a43dbaa1720cae4d0193b"
                            }
                        ],
                        [
                            {
                                "Tag": "Binary",
                                "Value": "Eq",
                                "Type_t": "Operator",
                                "Args": [
                                    {
                                        "Tag": "Identifier",
                                        "Value": "x",
                                        "Type_t": "Variable",
                                        "Args": None,
                                        "ID": "5bdd9c52ce3547d0a7542fef3604d0e1"
                                    },
                                    {
                                        "Tag": "Constant",
                                        "Value": "\"hello\"",
                                        "Type_t": "String",
                                        "Args": None,
                                        "ID": "97f42451401b4600abff70a4fcad98fd"
                                    }
                                ],
                                "ID": "5196eea5132840249d26b50abadca825"
                            }
                        ]
                    ]
                }
            ],
        },
        "Attributes": {}
    }

    methods = parse_class(ast["Methods"])
    attributes = parse_class(ast["Attributes"])
    param_t, typedefs, bindings = {}, {}, {}

    type_inference_test(methods, attributes, param_t, typedefs, bindings)

@should_fail
def test_parameter_type_mismatch():

    ast = {
        "Tag": "Class",
        "Value": "nil",
        "Type_t": "Class",
        "Args": None,
        "Name": "",
        "Base": "class",
        "ID": "1f9d089323e0446ba607abd71291c4d5",
        "Methods": {
            "ParameterMismatch": [
                {
                    "Tag": "Function",
                    "Value": "",
                    "Type_t": "Function",
                    "Args": None,
                    "Name": "ParameterMismatch",
                    "ID": "bb642a69c4924a07b471472137dcc7a0",
                    "Parameters": [
                        {
                            "Tag": "Parameter",
                            "Value": "x",
                            "Type_t": "",
                            "Args": None,
                            "ID": "33d1feb10715407e91d988d7a44d6d71"
                        }
                    ],
                    "Body": [
                        [
                            {
                                "Tag": "Binary",
                                "Value": "Eq",
                                "Type_t": "Operator",
                                "Args": [
                                    {
                                        "Tag": "Identifier",
                                        "Value": "x",
                                        "Type_t": "Variable",
                                        "Args": None,
                                        "ID": "33d1feb10715407e91d988d7a44d6d71"
                                    },
                                    {
                                        "Tag": "Constant",
                                        "Value": "\"hello\"",
                                        "Type_t": "String",
                                        "Args": None,
                                        "ID": "14eeb65ae9a74560815e7ed66b46ff1c"
                                    }
                                ],
                                "ID": "f55c62417fba4a62ade969e1c9b532c9"
                            }
                        ]
                    ]
                }
            ],
        },
        "Attributes": {}
    }

    methods = parse_class(ast["Methods"])
    attributes = parse_class(ast["Attributes"])
    param_t, typedefs, bindings = { "ParameterMismatch": {"x": SuTypes.Number} }, {}, {}

    type_inference_test(methods, attributes, param_t, typedefs, bindings)

@should_pass
def test_raw_type_equality():
    t1 = TypeRepr({'form': 'Primitive', 'name': 'Number', 'meaning': [SuTypes.Number]})
    t2 = TypeRepr({'form': 'Primitive', 'name': 'Number', 'meaning': [SuTypes.Number]})

    assert t1 == t2

    t1 = TypeRepr({'form': 'Primitive', 'meaning': [SuTypes.Date]})
    t2 = TypeRepr({'form': 'Primitive', 'meaning': [SuTypes.Boolean]})

    assert t1 != t2

    # t1 = TypeRepr({'form': 'Union', 'name': 'StrNum', 'meaning': [SuTypes.String, SuTypes.Number]})
    # t2 = TypeRepr({'form': 'Union', 'name': 'StrNum', 'meaning': [SuTypes.String, SuTypes.Number]})

    # assert t1 == t2





def main():
    test_single_line_type_mismatch()
    # test_single_variable_reassignment_valid()
    test_single_variable_reassignment()
    # test_parameter_type_mismatch()
    test_raw_type_equality()
    
if __name__ == "__main__":
    main()
