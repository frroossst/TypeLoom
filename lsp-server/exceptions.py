class TypeException(Exception):
    def __init__(self, msg):
        self.value = msg
        super().__init__(self.msg)

class MissingAttribute(TypeException):
    def __init__(self, attribute):
        msg = f"Missing attribute {attribute}"
        super().__init__(msg)

class ConflictingInferredTypes(TypeException):
    def __init__(self, node, existing, new):
        msg = f"Conflicting inferred types for {node}: existing {existing}, new {new}"
        super().__init__(msg)

class ConflictingDeclaredTypes(TypeException):
    def __init__(self, node, existing, new):
        msg = f"Conflicting declared types for {node}: existing {existing}, new {new}"
        super().__init__(msg)




    
