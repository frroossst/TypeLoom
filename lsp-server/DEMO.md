# Undeclared Class Variable
```
class()
    {
    MissingAttribute(x) 
        {
        .x = x
        }
    }
```
```
TypeError: Error in MissingAttribute at line 1:  Attribute x not found
```

# Variable reassignment
```
class()
    {
    Reassign()
        {
        x = "hello"
        x = 123
        }
    }
```
```
TypeError: Error in Reassign at line 2:  Conflicting inferred types for variable e3c08d1050474cbfbf13c23ff18b8761
existing: SuTypes.String, got: SuTypes.Number
```

# Parameter mismatch
```
// typdefinition for IncorrectParam in a separate file
type IncorrectParam >>= fn(x: Number) -> None
```
```
class()
    {
    IncorrectParam(x: Number) // this annotation only exists in the LSP as an in-line hint not actually in the code
        {
        x = "IAmAString"
        }
    }
```

```
TypeError: Conflicting inferred types for variable 17650a1119d644b3817651625465b494
existing: SuTypes.String, got: SuTypes.Number
```

# Type aliasing
```
type Number2 >>= Number
```
```
class()
    {
    SimplePrimitiveTypeAlias(a: Number2)
        {
        a = "thisShouldNotAssign"
        }
    }
```
```
TypeError: Conflicting inferred types for variable 56197b2885cc4e00846e891faa982fca
existing: SuTypes.Number, got: SuTypes.String
```

# Type inference and type error
```
class()
    {
    SimpleInferenceErrors(x: Number)
        {
        num = x + 123
        if Number?(x) and x > 100
            {
            // CODE
            }
        else
            {
            num() // ERROR
            }
        }
    }
```
```
TypeError: Type mismatch, expected function, got SuTypes.Number
```

# Runtime Guards
```
class()
    {
    SimpleRuntimeGuard(x: String)
        {
        if Number?(x)
            {
            num = x + 123
            }
        }
    }
```
```
TypeError: Conflicting inferred types. expected: SuTypes.String, got: SuTypes.Number
```

# String literal unions
```
type Currency >>= "USD" | "CAD" | "GBP"
```

```
class()
    {
	currencyTypeAlias()
			{
			u: Currency = "USD"
			nu: Currency = "usd" // ERROR: not a literal match
			ou: Currency = "other" // ERROR: not a literal match
			}
    }
```
```
TypeError: Conflicting inferred types for variable, existing SuTypes.String, got SuTypes.String ("usd")
```

# Structural Types
```
type User >>= #(name: String, age: Number)
type GetUserAuth >>= fn(usr: User)
```

```
class()
    {
    GetUserAuth(usr)
        {
        return true
        }
    }

GetUserAuth(Object(name: "Jane", age: "28"))
```
```
TypeError: Type structures do not match, expected (name: <SuTypes.String>, age: <SuTypes.Number>)
got: (name: <SuTypes.String>, age: <SuTypes.String>)
```




