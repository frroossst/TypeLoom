Most of the basic type inference is done in Go

While OCaml is used for more complex type inference, checking, and enforcement

The client and server in go lang as of now are quite redundant and should eventually
be merged into one singular HTTPS localhost server that takes in raw source code
from the VSCode frontend and interfaces with OCaml. 

===

# Types

## Function Types

Function return types and parameter types are never inferred, they are always explicitly declared by the programmer.
The type checker will however check that the inferred types match the declared types. In case of a conflict the declared 
types are considered to be correct and the inferred types are considered to be incorrect.


