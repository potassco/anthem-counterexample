"""
Module containing utilities for transformations.
"""

from typing import Sequence, Union

from clingo.ast import (
    AST,
    ASTType,
    Function,
    SymbolicAtom,
    Transformer,
    Position,
    Location,
    Aggregate,
    BodyAggregate,
    Rule,
    Literal,
    Sign,
    Disjunction,
)

from . import Predicate

# TODO: this has to be a new suffix (i.e. no predicate can end in this suffix)
PREDICATE_SUFFIX = "'"
# TODO: this needs to be a new predicate
UNSAT_PREDICATE = "unsat"

LOC = Location(Position("<string>", 1, 1), Position("<string>", 1, 1))


def apply_transformer(transformer: Transformer, prog: list[AST]) -> list[AST]:
    """
    Apply a transformer to a logic program.
    """
    ret = []
    for n in prog:
        x = transformer(n)
        if isinstance(x, list):
            ret.extend(x)
        else:
            ret.append(x)

    return ret


def atom_to_predicate(atom: AST) -> Predicate:
    """
    Get the predicate of an atom.
    """
    if atom.ast_type is not ASTType.SymbolicAtom:
        raise RuntimeError(f"Argument is not a symbolic atom {atom}")

    fun = atom.symbol

    return Predicate(fun.name, len(fun.arguments))


def map_atom(atom: AST) -> AST:
    """
    Map an atom to its auxiliary version.
    """
    if atom.ast_type is not ASTType.SymbolicAtom:
        raise RuntimeError(f"Argument is not a symbolic atom {atom}")

    fun = atom.symbol

    new_name = fun.name + PREDICATE_SUFFIX

    new_atom = SymbolicAtom(
        symbol=Function(
            location=fun.location,
            name=new_name,
            arguments=fun.arguments,
            external=fun.external,
        )
    )

    return new_atom


def unmap_atom(atom: AST) -> AST:
    """
    Undo the mapping of a predicate to its auxiliary version.
    """
    if atom.ast_type is not ASTType.SymbolicAtom:
        raise RuntimeError(f"Argument is not a symbolic atom {atom}")

    fun = atom.symbol
    new_name = fun.name.removesuffix(PREDICATE_SUFFIX)

    new_atom = SymbolicAtom(
        symbol=Function(
            location=fun.location,
            name=new_name,
            arguments=fun.arguments,
            external=fun.external,
        )
    )

    return new_atom


def is_mapped_predicate(atom: AST) -> bool:
    """
    Check whether an atom contains an auxiliary predicate.
    """
    if atom.ast_type is not ASTType.SymbolicAtom:
        raise RuntimeError(f"Argument is not a symbolic atom {atom}")

    name: str = atom.symbol.name
    return name.endswith(PREDICATE_SUFFIX)


def unsat_pred() -> str:
    """
    Get the string representing the auxiliary unsat predicate.
    """
    return UNSAT_PREDICATE


def choice_rule_for_elements(elements: Sequence[AST], body: Sequence[AST]) -> Rule:
    """
    Get a choice rule for the conditions of elements.
    """
    choice_elements = []
    for elem in elements:
        choice_elements.append(elem.condition)

    choice_head = Aggregate(
        location=LOC,
        left_guard=None,
        right_guard=None,
        elements=choice_elements,
    )

    choice_rule = Rule(location=LOC, head=choice_head, body=body)

    return choice_rule


def aggregate_constraint(aggregate: Union[Aggregate, BodyAggregate], body: Sequence[AST]) -> Rule:
    """
    Turn a body B and aggregate A into the constraint :- B, not A.
    """
    constraint_body = body
    constraint_body.append(
        Literal(
            location=LOC,
            sign=Sign.Negation,
            atom=aggregate,
        )
    )

    constraint = Rule(
        location=LOC,
        head=Disjunction(location=LOC, elements=[]),
        body=constraint_body,
    )

    return constraint
