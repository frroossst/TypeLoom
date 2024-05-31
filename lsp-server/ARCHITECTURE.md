The Go compiler for Suneido is used to generate an Abstract Syntax Tree (AST) from the source code. The AST is in a JSON format. 
The AST is then ingested by the type inference engine (currently written in Python, will later be ported to OCaml). When the AST is parsed
it creates graphs of all the inbuilt types and any custom types defined in the source code. Each variable or type is represented by a node in the graph.
The edges of the graph represent the constraints that exists. For example, "x must be of type Number". Since, the graphs of each distinct types
are separate from each other, the type inference engine can infer the type of each variable by traversing the graph and checking the constraints. A 
type conflict occurs when the type inference engine finds a variable that has two different types. This is resolved by checking the constraints
and determining which type is more specific. Each node contains it's inferred type, it's type constraints. During the inference stage the graphs are
produced, and during the checking stage the type constraints are checked. Objects are structurally typed. Unions are not exclusive ORs just regular ORs.
Intersections for objects are not types themselves but an additive combination of fields.

Only more specific newer constraints are stored. If a constraint, "x is of type Number" exists then it can only be replaced by a more specific constraint
such as, "x is of type i8" and not the other way around. 

Function names are mangled when a node is created. The typical scheme is className_visibility_functionName_parameterTypes_returnTypes
All functions and variables tagged with `@` are private, the number of `@` determines the scope for variables.


```
enum SuTypes {
    Any, 

    Boolean, 
    String, 
    Number, 
    Void,

    Function, 
    Object, 

    Unknown, 
    Never, 
}

enum Constraint {
    Union(Vec<SuTypes>),
    Intersection(Vec<SuTypes>),
}

struct Node {
    source_type: String,
    inferred_type: String,
    constraints: Vec<Constraint>,
}

struct WorkingTypes {
    root_nodes: HashMap<String, Node>,
}
```

# Verification

A combination of logging and runtime checks are used to verify the correctness of the type inference engine.


# Time and Memory Complexity






