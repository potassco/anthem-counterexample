"""
Utilities.
"""

from dataclasses import dataclass
from enum import Enum, auto

from clingo.ast import AST


@dataclass
class Programs:
    """
    Dataclass storing the program parts of the counterexample program.
    """

    left: list[AST]
    right: list[AST]
    generate: str
    difference: str
    public_reduct_left: list[AST] | None
    public_reduct_right: list[AST] | None


class Direction(Enum):
    """
    Enum representing directions of an equivalence problem.
    """

    UNIVERSAL = auto()
    FORWARD = auto()
    BACKWARD = auto()

    def includes_forward(self) -> bool:
        """Check if the direction includes forward."""
        return self in (Direction.UNIVERSAL, Direction.FORWARD)

    def includes_backward(self) -> bool:
        """Check if the direction includes backward."""
        return self in (Direction.UNIVERSAL, Direction.BACKWARD)

    @classmethod
    def from_string(cls, value: str) -> "Direction":
        match value:
            case "universal":
                return cls.UNIVERSAL
            case "forward":
                return cls.FORWARD
            case "backward":
                return cls.BACKWARD
            case _:
                raise ValueError(f"Invalid direction: {value}")


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


@dataclass
class Options:
    """
    Dataclass storing the options of the counterexample problem.
    """

    direction: Direction
    out_dir: str | None
    solve: bool
    start: int
    max_size: int | None
    use_gc: bool
    inputs: set[Predicate]
    outputs: set[Predicate]


def program_to_str(prog: list[AST], newline: bool = False) -> str:
    """
    Turn a program into its string representation.
    """
    string = "\n".join(str(n) for n in prog)

    # optionally add a newline at the end
    if newline:
        string += "\n"

    return string
