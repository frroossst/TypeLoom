# Gradual Type Systems

## Soundness

A sound type system will catch every type error that could happen at runtime. No false negatives,

## Completeness

A complete type system will accept any program that can't throw a type error at runtime. No false positives.

> NOTE: Gradual type systems needs to work well with idioms that predate the type system

There is a tradeoff between soundness and completeness

# Type Refinement

```
foo = function(x)                          // x: Any
    {
    x[0].Capitalize() // Type error!       // x: Any
    if String?(x)                          // x: String
        x[0].Capitalize() // No error
    }
```
Using existing language features and type guards to narrow down types or refine them.
Functions with side effects on the referenced value should drop the refinement and revert the type

> Types are scope-bound


