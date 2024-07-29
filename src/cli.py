import os.path
import argparse


d = (
    "======================================================================== \n"
    "  ___            ___ \n"
    " | _ \_____ __ _| _ \_  _ \n"
    " |   / -_) V  V /  _/ || |     \n"
    " |_|_\___|\_/\_/|_|  \_, |\n"
    "                     |__/ \n"
    "RewPy - Metadynamics Reweighting in Python \n"
    "Tiwary = Time-independent Free Energy Reconstruction \n"
    "based on the algorithm proposed by Tiwary and Parrinello JPCB 2014\n"
    "========================================================================= \n"
)


def parse_args(*args):
    parser = argparse.ArgumentParser(
        description=d, formatter_class=argparse.RawTextHelpFormatter
    )

    add_input_args(parser)
    add_output_args(parser)
    add_data_args(parser)
    add_legacy_args(parser)

    return parser.parse_args(*args)


def add_input_args(parser):
    group = parser.add_argument_group(
        "Input Options", "Options related to reading inputs."
    )

    group.add_argument(
        "-f",
        "--fes",
        required=True,
        help="FES filenames prefix as generated with plumed sum_hills --stride. \nExpects FPREF%%d.dat (default: %(default)s)",
    )
    group.add_argument(
        "-c",
        "--colvar",
        default="COLVAR",
        help="File containing original CVs, reweighting CVs and metadynamics bias",
    )
    group.add_argument(
        "-y",
        "--bias-factor",
        type=float,
        help=(
            "Biasfactor used in the well-tempered metadynamics, "
            "\nif omitted assumes a non-well-tempered metadynamics"
        ),
    )
    group.add_argument(
        "--kt",
        type=float,
        default=2.49,
        help="kT in the energy units of the FES files (default: %(default)s)",
    )
    group.add_argument(
        "--exp-bct-file",
        help="If provided, use precalculated ebetac list, if omitted use FES files",
    )


def add_output_args(parser):
    group = parser.add_argument_group(
        "Output Options", "Options related to saving files."
    )

    group.add_argument(
        "-o",
        "--outfile",
        default="fes_rew.dat",
        help="Output FES filename (default: %(default)s)",
    )

    group.add_argument(
        "--exp-bct-out", help="If provided, will save ebetac list into this file"
    )


def add_data_args(parser):
    group = parser.add_argument_group(
        "Extra Data Options", "Options related to calculations."
    )
    group.add_argument(
        "--cv-mins",
        type=float,
        nargs="+",
        help="Minimum values of the CV in colvar file, if omitted find it",
    )
    group.add_argument(
        "--cv-maxs",
        type=float,
        nargs="+",
        help="Naximum values of the CV in colvar file, if omitted find it",
    )
    group.add_argument(
        "--bins",
        type=int,
        nargs="+",
        help="Number of bins for the reweighted FES (default: %(default)s for each CV)",
    )
    group.add_argument("-v", "--verbose", action="store_true", help="be verbose")


def add_legacy_args(parser):
    group = parser.add_argument_group(
        "Legacy Options", "Pre v. 1.0 behaviour for numberical column selection:"
    )
    group.add_argument(
        "--num-fes",
        type=int,
        default=100,
        help="Number of FES input files (default: %(default)s)",
    )
    group.add_argument(
        "--fes-col",
        type=int,
        default=2,
        help="Free energy column in the FES input files \n(first column = 1) (default: %(default)s)",
    )
    group.add_argument(
        "--colvar-rew-col",
        type=int,
        nargs="+",
        default=[2],
        help="Column(s) in colvar file containing the CV to be reweighted \n(first column = 1) (default: %(default)s)",
    )
    group.add_argument(
        "--colvar-bias-col",
        type=int,
        nargs="+",
        default=[4],
        help="Column(s) in colvar file containing any energy bias \n(metadynamic bias, walls, external potentials..) \n(first column = 1) (default: %(default)s)",
    )


def setup_global_variables(args):
    # kT in energy units (kJ or kcal)
    kT = args.kt

    # biasfactor for Well-Tempered
    gamma = args.bias_factor

    # Well-Tempered Metadynamics or not
    is_well_tempered: bool = True
    if args.bias_factor is not None:
        if args.bias_factor > 0:
            is_well_tempered = True
        elif args.bias_factor == 0:
            raise Exception(
                (
                    "Bias factor of 0 is ambiguouse."
                    "\nHelp: \n\t If you ran with well-tempered metadynamics, check your value."
                    "\n\t If you did not run with well-tempered metadynamics, remove the -y/--bias_factor flag."
                )
            )
        elif args.bias_factor < 0:
            raise Exception("Bias factor can not be negative.")
    else:
        is_well_tempered = False
    # IF UPGRADING TO PYTHON 3.10 +
    # match args.bias_factor:
    # case _ if args.bias_factor > 0:
    # is_well_tempered = True
    # case _ if args.bias_factor == 0:
    # raise Exception((
    # "Bias factor of 0 is ambiguouse."
    # "\nHelp: \n\t If you ran with well-tempered metadynamics, check your value."
    # "\n\t If you did not run with well-tempered metadynamics, remove the -y/--bias_factor flag."
    # ))
    # case _ if args.bias_factor < 0:
    # raise Exception("Bias factor can not be negative.")
    # case _:
    # is_well_tempered = False

    # print some output while running
    verbose = args.verbose

    return kT, gamma, is_well_tempered, verbose


# CHECK IF NECESSARY FILES EXIST BEFORE STARTING
def verify_inputs(colvar_file, exp_beta_ct_file, num_fes_files, fes_file_prefix):
    if not os.path.isfile(colvar_file):
        print("ERROR: file %s not found, check your inputs" % colvar_file)
        exit(1)
    if exp_beta_ct_file:
        if not os.path.isfile(exp_beta_ct_file):
            print("ERROR: file %s not found, check your inputs" % exp_beta_ct_file)
            exit(1)
    else:
        for i in range(num_fes_files):
            fname = "%s%d.dat" % (fes_file_prefix, i)
            if not os.path.isfile(fname):
                print("ERROR: file %s not found, check your inputs" % fname)
                exit(1)
