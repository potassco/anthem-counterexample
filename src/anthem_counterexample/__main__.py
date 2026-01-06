"""
The main entry point for the application.
"""

import sys

from . import build_eqt, save_eqt_to_file, solve_for_counterexample
from .eqt import get_difference_program, get_generate_program, get_public_reduct
from .utils.logging import configure_logging, get_logger
from .utils.parse_program import parse_program
from .utils.parse_user_guide import parse_user_guide
from .utils.parser import get_parser


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
            print(f"{eqt_l2r}\n")
            print(f"{eqt_r2l}\n")
        else:
            # output to files
            save_eqt_to_file(eqt_l2r, args.save_to_files)
            save_eqt_to_file(eqt_r2l, args.save_to_files, False)
    else:
        # solve
        solve_for_counterexample(eqt_l2r, eqt_r2l, args.start, args.max)


if __name__ == "__main__":
    main()
