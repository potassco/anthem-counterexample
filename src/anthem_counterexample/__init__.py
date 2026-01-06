"""
The anthem_counterexample project.
"""

import os
from typing import Optional

from clingo.ast import AST
from clingo.control import Control
from clingo.solving import Model
from clingo.symbol import Symbol

from .eqt import DIFF_PREDICATE
from .utils import Predicate, program_to_str
from .utils.logging import get_logger
from .utils.transformation import PREDICATE_SUFFIX, UNSAT_PREDICATE

log = get_logger(__name__)


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


def save_eqt_to_file(eqt: str, out_dir: str, forward: bool = True) -> None:
    """
    Save the EQT program to the output directory.
    """
    direction = "forward" if forward else "backward"
    os.makedirs(out_dir, exist_ok=True)
    outfile = os.path.join(out_dir, f"{direction}.lp")
    log.info("Writing %s program to %s", direction, outfile)
    with open(outfile, "w", encoding="utf-8") as f:
        f.write(eqt)


def _symbol_to_predicate(symbol: Symbol) -> Predicate:
    return Predicate(symbol.name, len(symbol.arguments))


def _on_model(direction: str, size: int, inputs: set[Predicate], outputs: set[Predicate], model: Model) -> None:
    print(f"Found a counterexample for domain size {size} in the {direction} direction")
    symbols = model.symbols(atoms=True)
    counterexample_input = []
    stable_model = []
    model_public_reduct = []

    for symbol in symbols:
        pred = _symbol_to_predicate(symbol)

        # filter out diff predicate
        if pred.name == DIFF_PREDICATE:
            continue

        if pred.name == UNSAT_PREDICATE:
            model_public_reduct.append(str(symbol))

        if pred in inputs:
            counterexample_input.append(str(symbol))

        if pred in outputs:
            stable_model.append(str(symbol))

        if pred.name.endswith(PREDICATE_SUFFIX):
            original_predicate = Predicate(pred.name.removesuffix(PREDICATE_SUFFIX), pred.arity)
            if original_predicate in outputs:
                model_public_reduct.append(str(symbol))

    print("  Input for the counterexample:")
    print("    " + ", ".join(counterexample_input))

    print("  Stable model:")
    print("    " + ", ".join(stable_model))

    print("  Model of the public reduct:")
    print("    " + ", ".join(model_public_reduct))


def _solve_with_size(eqt: str, direction: str, size: int, inputs: set[Predicate], outputs: set[Predicate]) -> bool:
    """
    Solve an EQT program with the given domain size and return whether a counterexample was found.
    """
    ctl = Control(["-c", f"domain_size={size}"])
    ctl.add(eqt)
    ctl.ground()
    ret = ctl.solve(on_model=lambda m: _on_model(direction, size, inputs, outputs, m))

    return True if ret.satisfiable else False


def solve_for_counterexample(
    eqt_forward: Optional[str],
    eqt_backward: Optional[str],
    inputs: set[Predicate],
    outputs: set[Predicate],
    domain_start: int = 0,
    domain_max: Optional[int] = None,
):
    """
    Solve the given EQT programs for counterexamples by increasing the domain size from start to max.
    """
    domain_size = domain_start
    while True:
        # stop if the domain size is larger than the limit
        if domain_max is not None and domain_size > domain_max:
            print(f"No counterexample was found for the domain size max of {domain_max}")
            break

        print(f"Solving for counterexample of domain size {domain_size}")

        if eqt_forward:
            if _solve_with_size(eqt_forward, "forward", domain_size, inputs, outputs):
                break

        if eqt_backward:
            if _solve_with_size(eqt_backward, "backward", domain_size, inputs, outputs):
                break

        domain_size += 1
