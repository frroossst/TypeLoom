# Local inference

- works statement by statement

- type of a variable is inferred from the type of the expression used to initialize it

- cannot infer recursive types


# Bottom up inference

- works from the bottom of the AST to the top

- type of a variable is inferred from the type of the expression used to initialize it


# Top down checking

- works from the top of the AST to the bottom

- used to check against provided type annotations

