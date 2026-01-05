"""
Utilities.
"""

from dataclasses import dataclass

from clingo.ast import AST


@dataclass(frozen=True)
class Predicate:
    """
    Dataclass representing a predicate by its name and arity.
    """

    name: str
    arity: int

    def __str__(self) -> str:
        """Returns a string with the name/arity notation."""
        return f"{self.name}/{str(self.arity)}"


def program_to_str(prog: list[AST], newline: bool = False) -> str:
    """
    Turn a program into its string representation.
    """
    string = "\n".join(str(n) for n in prog)

    # optionally add a newline at the end
    if newline:
        string += "\n"

    return string
