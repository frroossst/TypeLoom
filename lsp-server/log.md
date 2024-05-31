# 23 November 2023

- basic python type inference
- did this in python as a proof of concept, future version in OCaml

```
function(x)
	{
	num = x + "123"
	num()
	}`
```
The above now throws a compile time error, as the type of num is inferred to be a string, and strings are not callable.
```
TypeError: For operator Add, "123" is not of type Number, it is of type String
```
Before it'd throw a runtime error,
```
ERROR uncaught in repl: can't convert String to number
```

```
function(x)
    {
    num = x + 123
    num()
    }`
```

```
TypeError: For operator Call, num is not of type Function, it is of type Number
```
Before it'd throw a runtime error,
```
ERROR uncaught in repl: can't call Number
```

Proof of concept shows that basic type inference is possible on Suneido without extensive changes to the language.

## Next steps
- [ ] parse and infer all primitive types  
- [ ] better error messages with line numbers and possible fixes
- [ ] all primitive parsing should be done in Go to avoid the need for yet another language and parser impl  
- [ ] start writing an OCaml inference engine  
- [ ] work on proof of soundness and completeness in Isabelle or Idris  
- [ ] start writing the white papaer  
- [ ] impl basic lsp in either vscode or nvim

# 22 December 2023

## Architecture

Every class has a key value store, this key value store stores the member identifier name has a key and the value is another
key value store that stores the relevant type information of it's scoped members/variables.

When the key value stores are built, they contain the primitive inferred types of the members/variables. 

Type inference uses the key value stores to infer the types of the members/variables, no type checking is done at this stage.

Type cheking is then later done to constriant solve the inferred types

## TODO

- [x] Implement typeFunction() parsing
- [x] Implement typeClass() parsing
- [x] Implement type key-value store

# 30 January 2024

Completed complete parsing of a class, including attributes and methods.

## TODO

- [ ] Implement developer defined types for function signatures
- [x] Implement type inference and graph construction
- [x] Implement type checking on graph constraints
- [x] Implement object structure parsing
- [ ] Implement attributes infers and checks
- [ ] Implement checks for binary eqs

# 5 February 2024

Separated infer and check, also, implemented graph and key value store

## TODO

- [x] Implement attributes infers and checks
- [x] Implement deep inference
- [ ] Implement checks for binary eqs
- [ ] Implement function signature parsing and developer defined types


# 8 February 2024

Using runtime checks for type inference might make the type system Turing Complete, need to look into this.

```
function(x, y) // 'a
    {
    num = x + 123 // type of x inferred to be number 'b
    if String?(x) and Number?(y)
        {
        // type of x inferred to be string
        num = x + y // adding a string and a number INVALID 'c
        }
    else 
        {
        num = "hello" // reassigning num to a string INVALID 'd
        }
    return num
    }

/*
no way to know if x is a string or a number via *only* inference

'b should throw if x is a string
'c should throw if x is a string
'd should throw if x is a number

'a should have the type specified via the developer and type annotations
runtime checks should only be used for variables that are not being "used" before said runtime checks
the type of a variable is immutable, so, num cannot be reassigned to a string

*/
```

## TODO

- [x] Implement a way to scope varibales local to a function (2 way mapping of IDs to identifier name)
- [ ] Implement function signature parsing and developer defined types
- [x] Add debug info and symbols


# 19 February 2024

Changed SuTypes interface to now use TypeRepr
Added a check to see if correct number of function parameters are typed
Added infer_generic to handle parentheses
Added Mul and Sub operator support
Added unit tests
Runtime type guards are sorta working (still run into comptime eval problem for types that are only known at runtime)
Implemented stricter equality checking

## TODO

- [ ] Implement union and intersection types
- [ ] Implement type aliasing
- [ ] Implement return types
- [ ] Implement type checking for function calls
- [ ] Implement stricter runtime type guards
- [ ] Implement DSL parser for type annotations
- [ ] Implement assertions and loggers for verification of type system

