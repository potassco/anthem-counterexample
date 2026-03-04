"""
The anthem_counterexample project.
"""

import os

from clingo.ast import AST
from clingo.control import Control
from clingo.solving import Model
from clingo.symbol import Symbol

from .utils import Predicate, program_to_str, Programs, Options
from .utils.logging import get_logger
from .utils.transformation import DIFF_PREDICATE, PREDICATE_SUFFIX, UNSAT_PREDICATE

log = get_logger(__name__)


def assemble_and_execute(programs: Programs, options: Options) -> None:
    """
    Assemble the counterexample program from its components and execute/output it.
    """
    if options.use_gc:
        _assemble_and_execute_gc(programs, options)
    else:
        _assemble_and_execute(programs, options)


def _assemble_and_execute(programs: Programs, options: Options) -> None:
    forward = None
    backward = None
    if options.direction.includes_forward():
        forward = build_eqt(programs.generate, programs.left, programs.public_reduct_right, programs.difference)  # type: ignore
    if options.direction.includes_backward():
        backward = build_eqt(programs.generate, programs.right, programs.public_reduct_left, programs.difference, False)  # type: ignore

    if options.solve:
        solve_for_counterexample(forward, backward, options.inputs, options.outputs, options.start, options.max_size)
    else:
        if options.out_dir:
            save_eqt_to_file(forward, options.out_dir)
            save_eqt_to_file(backward, options.out_dir)
        else:
            print(f"{forward}\n")
            print(f"{backward}\n")


def _assemble_and_execute_gc(programs: Programs, options: Options) -> None:
    forward_guess, forward_check = None, None
    backward_guess, backward_check = None, None
    if options.direction.includes_forward():
        forward_guess, forward_check = build_eqt_gc(
            programs.generate, programs.left, programs.public_reduct_right, programs.difference  # type: ignore
        )
    if options.direction.includes_backward():
        backward_guess, backward_check = build_eqt_gc(
            programs.generate, programs.right, programs.public_reduct_left, programs.difference, False  # type: ignore
        )

    if options.solve:
        solve_gc_for_counterexample(
            forward_guess,
            forward_check,
            backward_guess,
            backward_check,
            options.inputs,
            options.outputs,
            options.start,
            options.max_size,
        )
    else:
        if options.out_dir:
            save_eqt_gc_to_file(forward_guess, forward_check, options.out_dir)
            save_eqt_gc_to_file(backward_guess, backward_check, options.out_dir, False)
        else:
            print(f"{forward_guess}\n")
            print(f"{forward_check}\n")
            print(f"{backward_guess}\n")
            print(f"{backward_check}\n")


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


def save_eqt_gc_to_file(eqt_guess: str | None, eqt_check: str | None, out_dir: str, forward: bool = True) -> None:
    """
    Save the guess and check EQT program to the output directory.
    """
    if eqt_guess and eqt_check:
        save_eqt_to_file(eqt_guess, out_dir, forward, postfix="_guess")
        save_eqt_to_file(eqt_check, out_dir, forward, postfix="_check")


def save_eqt_to_file(eqt: str | None, out_dir: str, forward: bool = True, postfix: str | None = None) -> None:
    """
    Save the EQT program to the output directory.
    """
    if eqt:
        direction = "forward" if forward else "backward"
        os.makedirs(out_dir, exist_ok=True)
        outfile = os.path.join(out_dir, f"{direction}{postfix}.lp")
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

    return bool(ret.satisfiable)


def solve_for_counterexample(  # pylint: disable=too-many-positional-arguments
    eqt_forward: str | None,
    eqt_backward: str | None,
    inputs: set[Predicate],
    outputs: set[Predicate],
    domain_start: int = 0,
    domain_max: int | None = None,
) -> None:
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


def solve_gc_for_counterexample(  # pylint: disable=too-many-positional-arguments
    forward_guess: str | None,
    forward_check: str | None,
    backward_guess: str | None,
    backward_check: str | None,
    inputs: set[Predicate],
    outputs: set[Predicate],
    domain_start: int = 0,
    domain_max: int | None = None,
) -> None:
    """
    Solve the given guess and check EQT programs for counterexamples by increasing the domain size from start to max.
    """
    log.error("solving for guess and check not yet implemented")
