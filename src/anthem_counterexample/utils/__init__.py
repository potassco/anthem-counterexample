"""
Utilities.
"""

from dataclasses import dataclass
from enum import Enum, auto

from clingo.ast import AST

from .output import program_to_str


def build_eqt(generate: str, left: list[AST], public_reduct: list[AST], difference: str, forward: bool = True) -> str:
    """
    Build the EQT program as a string from the components.
    """
    eqt = (
        "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n"
        + f"% EQT {'forward' if forward else 'backward'}\n"
        + "% input generation\n"
        + generate
        + f"\n\n% {'left' if forward else 'right'} program\n"
        + program_to_str(left, True)
        + f"\n% public reduct of {'right' if forward else 'left'} program\n"
        + program_to_str(public_reduct, True)
        + "\n% difference detection\n"
        + difference
    )

    return eqt


def build_eqt_gc(
    generate: str, left: list[AST], public_reduct: list[AST], difference: str, forward: bool = True
) -> tuple[str, str]:
    """
    Build the guess and check EQT program as a string for the components.
    """
    eqt_guess = (
        "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n"
        + f"% EQT {'forward' if forward else 'backward'} guess\n"
        + "% input generation\n"
        + generate
        + f"\n\n% {'left' if forward else 'right'} program\n"
        + program_to_str(left, True)
    )
    eqt_check = (
        "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n"
        + f"% EQT {'forward' if forward else 'backward'} check\n"
        + f"% public reduct of {'right' if forward else 'left'} program\n"
        + program_to_str(public_reduct, True)
        + "\n% difference detection\n"
        + difference
    )

    return eqt_guess, eqt_check


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
        """Create a Direction object from a string."""
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
class Options:  # pylint: disable=too-many-instance-attributes
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
