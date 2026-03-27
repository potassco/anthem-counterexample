"""
Module for checking for naming conflicts of predicates.
"""

from clingo.ast import AST, Transformer

from . import Predicate
from .logging import get_logger
from .transformation import atom_to_predicate

log = get_logger(__name__)


def check_and_rename_privates(
    left: list[AST], right: list[AST], publics: set[Predicate]
) -> tuple[list[AST], list[AST]]:
    """
    Check if the private predicates of the programs are distinct and rename conflicting predicates if necessary.
    """
    privates_left = _collect_privates(left, publics)
    privates_right = _collect_privates(right, publics)
    conflicts = _conflicting_predicates(privates_left, privates_right)
    if conflicts:
        log.error("Renaming of conflicting private predicates not yet supported")
        raise RuntimeError(f"Found conflicting private predicates: {conflicts}")

    return left, right


def _collect_privates(program: list[AST], publics: set[Predicate]) -> set[Predicate]:
    collector = PrivatePredicateCollector(publics)
    for n in program:
        collector(n)

    return collector.privates


def _conflicting_predicates(left: set[Predicate], right: set[Predicate]) -> set[Predicate]:
    return left & right


class PrivatePredicateCollector(Transformer):
    """
    Class to collect the private predicates of a program.
    """

    def __init__(self, publics: set[Predicate]) -> None:
        super().__init__()
        self.publics = publics
        self.privates: set[Predicate] = set()

    def visit_SymbolicAtom(self, node: AST) -> AST:  # pylint: disable=invalid-name
        """
        Add the predicate of a symbolic atom to the privates if it is not public.
        """
        pred = atom_to_predicate(node)
        if pred not in self.publics:
            self.privates.add(pred)

        return node
