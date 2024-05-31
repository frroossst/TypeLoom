from typing import Callable

"""
λf.λg.λx.f (g x) 
"""

# Define the function that takes f and returns it
def compose_f(f: Callable[[int], int]) -> Callable[[int], int]:
    return f

# Define the function that takes g and returns it
def compose_g(g: Callable[[int], int]) -> Callable[[int], int]:
    return g

# Define the function that takes f, g, and x and applies f to the result of g(x)
def compose_x(f: Callable[[int], int], g: Callable[[int], int], x: int) -> int:
    return f(g(x))

# Now you can use this to compose functions
# Let's define two simple functions for demonstration
def double(x: int) -> int:
    return x * 2

def increment(x: int) -> int:
    return x + 1

# Now we can use the compose function to create a new function
f = compose_f(increment)
g = compose_g(double)

# And we can use this new function on an input
result = compose_x(f, g, 5)  # Output: 11

print(result)

