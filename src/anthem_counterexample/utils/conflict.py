"""
Module for checking for naming conflicts of predicates.
"""

from clingo.ast import AST, Transformer

from . import Auxiliaries, Predicate
from .logging import get_logger
from .transformation import atom_to_predicate

log = get_logger(__name__)


def check_and_rename_auxiliaries(
    left: list[AST], right: list[AST], publics: set[Predicate], aux: Auxiliaries
) -> Auxiliaries:
    privates = _collect_privates(left + right, publics)
    predicates = publics | privates
    conflict_predicates = _conflicting_predicates(predicates, aux.predicates())
    if conflict_predicates:
        replacements, predicates = _get_replacements(conflict_predicates, predicates)
        aux = aux.replace_values(replacements)

    placeholders = _collect_placeholders(left + right)
    if aux.size in placeholders:
        log.error("Renaming of size placegolder not yet supported")
        raise RuntimeError("Size placeholder conlficts with a placeholder in the programs")

    if _contains_suffix(publics | privates, aux.suffix):
        log.error("Renaming of the predicate suffix not yet supported")
        raise RuntimeError("Predicate suffix conflicting with some predicate name")

    return aux


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
        replacements, _ = _get_replacements(conflicts, publics | privates_left | privates_right)

        log.error("Renaming of conflicting private predicates not yet supported")
        raise RuntimeError(f"Found conflicting private predicates: {[str(p) for p in conflicts]}")

        right = _replace_predicates(right, replacements)

    return left, right


def _get_replacements(
    conflicts: set[Predicate], predicates: set[Predicate]
) -> tuple[dict[Predicate, Predicate], set[Predicate]]:
    pred_replacements = {}
    for pred in conflicts:
        new = _get_replacement_predicate(pred, predicates)
        pred_replacements[pred] = new
        predicates.add(new)
        log.debug("Replacement for %s is %s", pred, new)
    return pred_replacements, predicates


def _get_replacement_predicate(base: Predicate, predicates: set[Predicate]) -> Predicate:
    """
    Get a replacement predicate for base that does not conflict with predicates.
    """
    i = 0
    new = Predicate(base.name + f"__{i}", base.arity)
    while new in predicates:
        i += 1
        new = Predicate(base.name + f"__{i}", base.arity)

    return new


def _replace_predicates(program: list[AST], replacements: dict[Predicate, Predicate]) -> list[AST]:
    """
    Replace all predicates that are part of the replacement dictionary.
    """


def _collect_placeholders(program: list[AST]) -> set[str]:
    log.error("Collect placeholder not yet implemented")
    return set()


def _collect_privates(program: list[AST], publics: set[Predicate]) -> set[Predicate]:
    collector = PrivatePredicateCollector(publics)
    for n in program:
        collector(n)

    return collector.privates


def _conflicting_predicates(left: set[Predicate], right: set[Predicate]) -> set[Predicate]:
    return left & right


def _contains_suffix(predicates: set[Predicate], suffix: str) -> bool:
    for p in predicates:
        if p.name.endswith(suffix):
            return True
    return False


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
