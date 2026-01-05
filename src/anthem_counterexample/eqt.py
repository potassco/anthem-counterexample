"""
Module to get counterexample program.
"""

from clingo.ast import AST

from .transformation import (
    ChoiceElementNormalizer,
    ChoiceGuardNormalizer,
    HeadAggregateNormalizer,
    RejectDisjunctions,
    RemoveHeadCondition,
    RemoveHeadNegation,
    ReplacePositiveOutputPredicates,
    TransformRuleHeads,
)
from .utils import Predicate, program_to_str
from .utils.transformation import apply_transformer, unsat_pred, PREDICATE_SUFFIX
from .utils.logging import get_logger

log = get_logger(__name__)


def _normalize_program(prog: list[AST]) -> list[AST]:
    """
    Normalize a logic program.
    """
    for t in [
        RejectDisjunctions,
        RemoveHeadCondition,
        HeadAggregateNormalizer,
        ChoiceGuardNormalizer,
        ChoiceElementNormalizer,
        RemoveHeadNegation,
    ]:
        prog = apply_transformer(t(), prog)
        log.debug("Program after applying %s", t.__name__)
        log.debug(program_to_str(prog, True))

    return prog


def _public_reduct(prog: list[AST], outputs: set[Predicate]) -> list[AST]:
    """
    Compute the public reduct of a program with respest to a set of output predicates.
    """
    for t in [ReplacePositiveOutputPredicates, TransformRuleHeads]:
        prog = apply_transformer(t(outputs), prog)
        log.debug("Program after applying %s", t.__name__)
        log.debug(program_to_str(prog, True))

    return prog


def get_generate_program(inputs: set[Predicate]) -> str:
    """
    Get the program to generate inputs.
    """
    # start constructing the program as a list of rules (represented as strings)
    prog = ["#const n=0.", "dom(1..n)."]

    for pred in inputs:
        # construct list of variables (i.e. X0, X1, ...) and body (i.e. dom(X0), dom(X1), ...)
        body = ""
        variables = ""
        for i in range(pred.arity):
            var = f"X{i}"
            if i > 0:
                body += ", "
                variables += ","
            body += f"dom({var})"
            variables += var

        # add choice rule for the predicate
        if pred.arity == 0:
            prog.append(f"{{ {pred.name} }}.")
        else:
            prog.append(f"{{ {pred.name}({variables}) }} :- {body}.")

    # turn the list into a string
    prog_str = "\n".join(prog)

    log.debug("Generate program")
    log.debug(prog_str + "\n")

    return prog_str


def get_difference_program(outputs: set[Predicate]) -> str:
    """
    Get the program to detect differences in outputs.
    """
    # construct the program as a list of rules (strings)
    prog = []

    for pred in outputs:
        if pred.arity == 0:
            # add propositional difference rules
            prog.append(f"diff :- {pred.name}, not {pred.name}{PREDICATE_SUFFIX}.")
            prog.append(f"diff :- not {pred.name}, {pred.name}{PREDICATE_SUFFIX}.")
        else:
            # get a list of variables matching the arity of pred
            variables = ""
            for i in range(pred.arity):
                var = f"X{i}"
                if i > 0:
                    variables += ","
                variables += var

            # add difference rules with variables
            prog.append(f"diff :- {pred.name}({variables}), not {pred.name}{PREDICATE_SUFFIX}({variables}).")
            prog.append(f"diff :- not {pred.name}({variables}), {pred.name}{PREDICATE_SUFFIX}({variables}).")

    # detect the unsat predicate as a difference
    prog.append(f"diff :- {unsat_pred()}.")

    # enforce a counterexample
    prog.append(":- not diff.")

    # represent the program as a string
    prog_str = "\n".join(prog)

    log.debug("Difference program")
    log.debug(prog_str + "\n")

    return prog_str


def get_public_reduct(prog: list[AST], outputs: set[Predicate]) -> list[AST]:
    """
    Get the public reduct of the program in filename.
    """
    return _public_reduct(_normalize_program(prog), outputs)
