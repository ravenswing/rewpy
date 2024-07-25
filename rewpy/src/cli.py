import os.path
import argparse


d = """
========================================================================
Time-independent Free Energy reconstruction script (a.k.a. reweight)
based on the algorithm proposed by Tiwary and Parrinello JPCB 2014

Typical usages:

1) to project your metadynamics FES on CVs you did not
   bias during your metadynamics run

2) to estimate the error on your FE profiles by comparing them with
   the FE profiles obtained integrating the metadynamics bias
   e.g. using plumed sum_hills


Example:

reweight.py -bsf 5.0 -kt 2.5 -fpref fes2d- -nf 80 -fcol 3 
            -colvar COLVAR -biascol 4 -rewcol 2 3

takes as input 80 FES files: fes2d-0.dat, fes2d-1.dat, ..., fes2d-79.dat 
obtained using a well-tempered metadynamics with bias factor 5
and containing the free energy in the 3rd column and the COLVAR file
containing the bias in the 4th column and outputs the FES projected 
on the CVs in column 2 and 3 of COLVAR file.

Ludovico Sutto
l.sutto@ucl.ac.uk                                       v1.0 - 23/04/2015

Added Python 3 compatibility, loading from and saving of ebetac files
which allows sidestepping the fes files for repeated reweighting from
the same simulation, and the option to specify bin size for each CV
independently.

New options: -ebetac <filename>, -savelist <filename>

Ladislav Hovan
ladislav.hovan.15@ucl.ac.uk                             v2.0 - 30/01/2019
=========================================================================
"""


def parse_args(*args):
    parser = argparse.ArgumentParser(description=d)

    add_input_args(parser)
    add_output_args(parser)
    add_data_args(parser)

    return parser.parse_args(*args)


def add_input_args(parser):
    group = parser.add_argument_group(
        "Input Options", "Options related to reading inputs."
    )
    group.add_argument(
        "-bsf",
        type=float,
        help="biasfactor used in the well-tempered metadynamics, if omitted assumes a non-well-tempered metadynamics",
    )
    group.add_argument(
        "-kt",
        type=float,
        default="2.49",
        help="kT in the energy units of the FES files (default: %(default)s)",
    )
    group.add_argument(
        "-fpref",
        default="fes",
        help="FES filenames prefix as generated with plumed sum_hills --stride. Expects FPREF%%d.dat (default: %(default)s)",
    )
    group.add_argument(
        "-nf",
        type=int,
        default=100,
        help="number of FES input files (default: %(default)s)",
    )
    group.add_argument(
        "-fcol",
        type=int,
        default=2,
        help="free energy column in the FES input files (first column = 1) (default: %(default)s)",
    )
    group.add_argument(
        "-ebetac", help="use precalculated ebetac list, if omitted use FES files"
    )
    group.add_argument(
        "-colvar",
        default="COLVAR",
        help="filename containing original CVs, reweighting CVs and metadynamics bias",
    )
    group.add_argument(
        "-rewcol",
        type=int,
        nargs="+",
        default=[2],
        help="column(s) in colvar file containing the CV to be reweighted (first column = 1) (default: %(default)s)",
    )
    group.add_argument(
        "-biascol",
        type=int,
        nargs="+",
        default=[4],
        help="column(s) in colvar file containing any energy bias (metadynamic bias, walls, external potentials..) (first column = 1) (default: %(default)s)",
    )


def add_output_args(parser):
    group = parser.add_argument_group(
        "Output Options", "Options related to saving files."
    )
    group.add_argument("-savelist", help="save ebetac list into this file")
    group.add_argument(
        "-outfile",
        default="fes_rew.dat",
        help="output FES filename (default: %(default)s)",
    )


def add_data_args(parser):
    group = parser.add_argument_group(
        "Extra Data Options", "Options related to calculations."
    )
    group.add_argument(
        "-min",
        type=float,
        nargs="+",
        help="minimum values of the CV in colvar file, if omitted find it",
    )
    group.add_argument(
        "-max",
        type=float,
        nargs="+",
        help="maximum values of the CV in colvar file, if omitted find it",
    )
    group.add_argument(
        "-bin",
        type=int,
        nargs="+",
        help="number of bins for the reweighted FES (default: %(default)s for each CV)",
    )
    group.add_argument("-v", "--verbose", action="store_true", help="be verbose")


def setup_global_variables(args):
    # kT in energy units (kJ or kcal)
    kT = args.kt

    # biasfactor for Well-Tempered
    gamma = args.bsf

    # Well-Tempered Metadynamics or not
    if args.bsf is not None and args.bsf > 0:
        is_well_tempered = True
    else:
        is_well_tempered = False

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
