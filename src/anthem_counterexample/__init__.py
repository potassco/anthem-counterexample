"""
The anthem_counterexample project.
"""

import os
from typing import Optional

from clingo.ast import AST
from clingo.control import Control

from .utils import program_to_str
from .utils.logging import get_logger

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


def _solve_with_size(eqt: str, size: int) -> bool:
    """
    Solve an EQT program with the given domain size and return whether a counterexample was found.
    """
    ctl = Control(["-c", f"domain_size={size}"])
    ctl.add(eqt)
    ctl.ground()
    # TODO: add custom on_model function
    ret = ctl.solve(on_model=print)

    return True if ret.satisfiable else False


def solve_for_counterexample(
    eqt_forward: Optional[str], eqt_backward: Optional[str], domain_start: int = 0, domain_max: Optional[int] = None
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
            if _solve_with_size(eqt_forward, domain_size):
                print(f"Found a counterexample in the forward direction of size {domain_size}")
                break

        if eqt_backward:
            if _solve_with_size(eqt_backward, domain_size):
                print(f"Found a counterexample in the backward direction of size {domain_size}")
                break

        domain_size += 1
