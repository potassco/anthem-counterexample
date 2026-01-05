"""
The anthem_counterexample project.
"""

import os

from clingo.ast import AST

from .utils import program_to_str
from .utils.logging import get_logger

log = get_logger(__name__)


def build_eqt(generate: str, left: list[AST], public_reduct: list[AST], difference: str, forward: bool = True) -> str:
    """
    Build the EQT program as a string from the components.
    """
    eqt = (
        f"% EQT {'forward' if forward else 'backward'}\n"
        + "% input generation\n"
        + generate
        + f"\n\n% {'left' if forward else 'right'} program\n"
        + program_to_str(left, True)
        + f"\n%public reduct of {'right' if forward else 'left'} program\n"
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
