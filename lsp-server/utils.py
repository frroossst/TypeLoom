def todo(str = ""):
    raise NotImplementedError(f"TODO {str}")

def unimplemented(str = ""):
    raise NotImplementedError(f"Unimplemented: {str}")

class DebugInfo:

    func_name = None
    line_num = None

    def __init__(self) -> None:
        pass

    def set_func(self, func_name) -> None:
        self.func_name = func_name

    def set_line(self, line_num) -> None:
        self.line_num = line_num

    def trigger(self, e, msg = ""):
        raise TypeError(f"Error in {self.func_name}() at line {self.line_num}: {msg} {e}") from e

