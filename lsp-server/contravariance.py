from typing import Callable

# A simple example to explain contravariance in Python

class Animal:
    def __init__(self) -> None:
        pass

class Mammal(Animal):
    def __init__(self) -> None:
        pass

class Human(Mammal):
    def __init__(self) -> None:
        pass



def f(g: Callable[[Mammal], Mammal]) -> None:
    return None

def g(_: Animal) -> Human:
    return Human()

def main():
    f(g)

if __name__ == "__main__":
    main()
