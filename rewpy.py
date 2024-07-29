import numpy as np

from src import cli
from src import tiwary
from src import io


def main() -> None:
    args = cli.parse_args()

    kT, gamma, is_well_tempered, verbose = cli.setup_global_variables(args)

    # INPUT ARGUMENTS
    # Prefix for the input FES files (before number.dat)
    fes_file_prefix = args.fes
    # Number of FES files generated with sum_hills stride option (the more the better)
    num_fes_files = args.num_fes
    # Column in FES file corresponding to the Free Energy
    # NB: the first column is 0
    fes_column_free = args.fes_col - 1

    # Name of the file containing the CVs on which to project the FES and the bias
    colvar_file = args.colvar_file
    # List with the columns of the CVs on which to project the FES
    # NB: the first column is 0
    colvar_rew_columns = [i - 1 for i in args.rewcol]
    rew_dimension = len(colvar_rew_columns)
    # List with column numbers of your colvar_file containing the bias
    # and any external bias/restraint/walls --> CHECK
    # NB: the first column is 0
    colvar_bias_columns = [i - 1 for i in args.biascol]

    # Minimum and maximum bounds of the CVs in the input
    # NB: if I don't define -min or -max in the input, I will find their value scanning the COLVAR file
    # s_min = args.min
    # s_max = args.max

    # Optional: provide ebetac file for loading
    exp_beta_ct_file = args.ebetac

    ### OUTPUT ARGUMENTS
    # Output FES filename
    output_file = args.outfile
    # Optional: ebetac file for saving
    exp_beta_ct_save = args.savelist

    # Grid size for the reweighted FES
    if args.bin:
        assert (
            len(args.bin) == rew_dimension
        ), f"ERROR: the number of -bin provided ({len(args.bin)}) does not match the dimension of reweighting CVs ({rew_dimension})"
        grid_shape = args.bin
    else:
        grid_shape = [100] * rew_dimension

    cli.verify_inputs(colvar_file, exp_beta_ct_file, num_fes_files, fes_file_prefix)

    if exp_beta_ct_file:
        exp_beta_ct = list(np.loadtxt(exp_beta_ct_file))
    else:
        exp_beta_ct = tiwary.calculate_ct(
            num_fes_files,
            fes_file_prefix,
            fes_column_free,
            verbose,
            is_well_tempered,
            gamma,
            kT,
        )

    if exp_beta_ct_save:
        np.savetxt(exp_beta_ct_save, exp_beta_ct)

    cv_ranges_min, cv_ranges_max = tiwary.calculate_cv_ranges(
        colvar_file,
        rew_dimension,
        colvar_rew_columns,
        verbose,
    )

    fes, s_grid = tiwary.boltzmann_sampling(
        colvar_file,
        cv_ranges_min,
        cv_ranges_max,
        rew_dimension,
        grid_shape,
        colvar_rew_columns,
        num_fes_files,
        colvar_bias_columns,
        exp_beta_ct,
        verbose,
        kT,
    )

    io.save_output(output_file, rew_dimension, s_grid, fes, verbose)


if __name__ == "__main__":
    main()
