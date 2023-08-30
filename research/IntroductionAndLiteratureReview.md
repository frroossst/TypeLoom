# Introduction

Programming languages can be classified into two broad categories based on their type systems: static and dynamic. 

Static languages require explicit type declarations for variables and functions, and check the type compatibility at compile time, some examples of 
such languages include C, C++, Rust, Java. Dynamic languages, on the other hand, infer the types of values at run time, and allow more flexibility 
and expressiveness, some example of these are Python, Ruby, Javascript. However, dynamic languages also have some drawbacks, such as the lack of 
type safety, performance, compile time error checking.

To overcome these limitations, some researchers have proposed the idea of gradual typing, which is a type system that allows both static and 
dynamic typing in the same language, as the name suggests it is the idea of gradually introducing types to a code base written in a language that is
dynamically typed. Gradual typing enables programmers to annotate their code with optional type information, and use static or dynamic checking 
depending on the presence or absence of annotations. Gradual typing can also facilitate the migration of legacy code from dynamic to static typing, 
by allowing incremental and partial type annotations. Optional typing is the idea of allowing programmers to choose if they want to use the type system
or not.

However, adding gradual typing to an existing language is not a trivial task. It requires modifying the syntax, semantics, and implementation of the 
language, which more often than not introduces backwards compatibility issues, performance overheads, and maintainability challenges. 
Moreover, gradual typing may not be suitable for all kinds of legacy code bases, especially those that rely heavily on dynamic features or idioms that 
are hard to type to model using a type system that may or may not be expressive enough.

In this research project, I propose a novel approach to introduce gradual typing to a legacy code base using an LSP (Language Server Protocol). 
A LSP is a standard protocol that defines the communication between an editor or an IDE and a language server that provides language features such as 
code completion, syntax highlighting, error checking, etc. 

# Proposal

Languages like Python add additional syntax to support optional typing.
```
// Snippet that is not typed; here x can be a number, string, or any other type
def foo(x):
    return x + 1

// Snippet that is typed; here x is an integer and the function bar returns an integer
def bar(x: int) -> int:
    return x + 1
```

Languages like Typescript leverage a transpiler that constructs a whole new superset of language that supports optional typing. As a result of the 
approach languages like typescript takes, every valid piece of Javascript code is also a valid Typescript code, but not the other way around!

```
// Snippet that is not typed; here x can be a number, string, or any other type
function foo(x) {
    return x + 1;
}

// Snippet that is typed; here x is an integer and the function bar returns an integer
function bar(x: number): number {
    return x + 1;
}
```

My approach leverages LSP to implement gradual typing as a language server that interacts with the editor or IDE, without requiring any changes to the 
original language or compiler. This way, we can provide optional and gradual typing to any legacy code base that supports LSP, regardless of the 
underlying language or platform.


# Literature Review

Gradual typing was first introduced by Siek and Taha [1](http://scheme2006.cs.uchicago.edu/13-siek.pdf), who defined a formal model of gradual typing based on a simple functional language. 
They also proposed a consistency relation between static and dynamic types, which is used to determine when a type conversion is needed at run time. 

Later, Siek et al [2](http://aszt.inf.elte.hu/~gsd/s/cikkek/concepts/2007/gradual-obj.pdf) extended the model to support object-oriented features such as classes, inheritance, and polymorphism.

Several languages have adopted gradual typing as a way to combine static and dynamic typing in the same language. For example, 
TypeScript [3](https://web.stanford.edu/class/cs242/materials/readings/siek06__gradual.pdf) is a superset of JavaScript that adds optional static types and transpiles to plain JavaScript. 
Similarly, Hack [4](https://engineering.fb.com/2014/03/20/developer-tools/hack-a-new-programming-language-for-hhvm/) is a dialect of PHP that adds gradual typing and runs on the HHVM platform [5](https://dl.acm.org/doi/pdf/10.1145/3192366.3192374). 
Other examples include Typed Racket, Typed Clojure, Dart, etc.

One of them is the performance overhead caused by run-time type checks. To address this issue, some researchers have proposed various optimization 
techniques, such as JIT compilation [6](https://wphomes.soic.indiana.edu/jsiek/files/2014/03/retic-python.pdf), selective compilation [7](https://dl.acm.org/doi/10.1145/2914770.2837630), hybrid monitoring [8](https://arxiv.org/pdf/1802.06375v1.pdf), etc. Another challenge is the usability of gradual
typing, especially for novice programmers who may not be familiar with type systems or annotations. To improve the usability of gradual typing, 
some researchers have proposed tools such as type inference [9](https://link.springer.com/chapter/10.1007/11531142_19), type error diagnosis [10](https://web.engr.oregonstate.edu/~erwig/papers/CF-Typing_POPL14.pdf), type migration [11](https://www.researchgate.net/publication/355438129_Solver-based_gradual_type_migration), etc.

This approach differs from the existing work on gradual typing in two aspects. 

First, we do not modify the original language or compiler to support gradual typing. Instead, we implement gradual typing as a language server that 
communicates with the editor or IDE via the Language Server Protocol (LSP). This way, we can avoid compatibility issues, performance overheads, and 
implementation difficulties that may arise from changing the language or compiler. 

Second, we do not impose any restrictions on the dynamic features or idioms that can be used in the legacy code base. Instead, we use LSP to provide 
feedback and guidance to the programmers on how to annotate their code with optional types. This way, we can accommodate any kind of legacy code base 
that supports LSP, regardless of the underlying language or platform. And the types can easily be stored in a database or file(s) and can hook into the
existing version control systems like git, svn, etc.
