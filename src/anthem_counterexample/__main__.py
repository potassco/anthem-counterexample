"""
The main entry point for the application.
"""

import sys

from clingo.control import Control

from . import build_eqt, save_eqt_to_file
from .utils.logging import configure_logging, get_logger
from .utils.parse_user_guide import parse_user_guide
from .utils.parse_program import parse_program
from .utils.parser import get_parser
from .eqt import get_generate_program, get_public_reduct, get_difference_program


def main() -> None:
    """
    Run the main function.
    """
    # argument parser
    parser = get_parser()
    args = parser.parse_args()

    # logging
    configure_logging(sys.stderr, args.log, sys.stderr.isatty())
    log = get_logger("main")

    # parsing user guide and program
    inputs, outputs = parse_user_guide(args.user_guide)
    left = parse_program(args.left)
    right = parse_program(args.right)

    # get components of EQT
    generate = get_generate_program(inputs)
    public_reduct_right = get_public_reduct(parse_program(args.right), outputs)
    public_reduct_left = get_public_reduct(parse_program(args.left), outputs)
    difference = get_difference_program(outputs)

    # assemble EQT programs
    eqt_l2r = build_eqt(generate, left, public_reduct_right, difference)
    eqt_r2l = build_eqt(generate, right, public_reduct_left, difference, False)

    if args.no_solve:
        if not args.save_to_files:
            # output to console
            print(eqt_l2r)
            print()
            print(eqt_r2l)
        else:
            # output to files
            save_eqt_to_file(eqt_l2r, args.save_to_files)
            save_eqt_to_file(eqt_r2l, args.save_to_files, False)
    else:
        # solve
        log.warning("solving not yet supported")


if __name__ == "__main__":
    main()
