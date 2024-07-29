import numpy as np
from math import exp, ceil

# Tiwary and Parrinello JPCB 2014
# Acknowledgements for previous versions:
# L. Sutto  l.sutto@ucl.ac.uk                    v1.0 - 23/04/2015
# L. Hovan  ladislav.hovan.15@ucl.ac.uk          v2.0 - 30/01/2019


# FIRST PART: calculate c(t)
def calculate_ct(
    num_fes_files,
    fes_file_prefix,
    fes_column_free,
    verbose,
    is_well_tempered,
    gamma,
    kT,
):
    # This part is independent on the number of CVs being biased
    # c(t) represents an estimate of the reversible
    # work performed on the system until time t
    if verbose:
        print("Reading FES files...")

    # calculates ebetac = exp(beta c(t)), using eq. 12 in eq. 3 in the JPCB paper
    ebetac = []
    for i in range(num_fes_files):
        if verbose and num_fes_files > 10 and i % (num_fes_files // 10) == 0:
            print(
                "%d of %d (%.0f%%) done"
                % (i, num_fes_files, (i * 100.0 / num_fes_files))
            )

        ########################################
        # set appropriate format for FES file names, NB: i starts from 0
        fname = "%s%d.dat" % (fes_file_prefix, i)
        # fname = '%s.%d' % (fes_file_prefix,i+1)
        ########################################

        data = np.loadtxt(fname)
        s1, s2 = 0.0, 0.0
        if is_well_tempered:
            for p in data:
                exponent = -p[fes_column_free] / kT
                s1 += exp(exponent)
                s2 += exp(exponent / gamma)
        else:
            for p in data:
                s1 += exp(-p[fes_column_free] / kT)
            s2 = len(data)
        ebetac.append(s1 / s2)

    # this would be c(t):
    # coft = [ kT*log(x) for x in ebetac ]

    return ebetac


def calculate_cv_ranges(
    colvar_file, rew_dimension, colvar_rew_columns, s_min, s_max, verbose
):
    if verbose:
        print("Calculating CV ranges..")

    # NB: loadtxt takes care of ignoring comment lines starting with '#'
    colvar = np.loadtxt(colvar_file)

    # find min and max of rew CV
    calc_smin = False
    calc_smax = False

    if not s_min:
        s_min = [9e99] * rew_dimension
        calc_smin = True
    if not s_max:
        s_max = [-9e99] * rew_dimension
        calc_smax = True

    for row in colvar:
        for i in range(rew_dimension):
            col = colvar_rew_columns[i]
            val = row[col]

            if calc_smin:
                if val < s_min[i]:
                    s_min[i] = val
            if calc_smax:
                if val > s_max[i]:
                    s_max[i] = val

    if verbose:
        for i in range(rew_dimension):
            print("CV[%d] range: %10.5f ; %10.5f" % (i, s_min[i], s_max[i]))

    return s_min, s_max


# SECOND PART: Boltzmann-like sampling for reweighting
def boltzmann_sampling(
    colvar_file,
    s_min,
    s_max,
    rew_dimension,
    grid_shape,
    colvar_rew_columns,
    num_fes_files,
    colvar_bias_columns,
    ebetac,
    verbose,
    kT,
):
    # Load the colvar file into a numpy array
    # NB: loadtxt takes care of ignoring comment lines starting with '#'
    colvar = np.loadtxt(colvar_file)

    # Build the new square grid for the reweighted FES
    s_grid = [[]] * rew_dimension
    for i in range(rew_dimension):
        ds = (s_max[i] - s_min[i]) / (grid_shape[i] - 1)
        s_grid[i] = [s_min[i] + n * ds for n in range(grid_shape[i])]
        if verbose:
            print("Grid ds CV[%d]=%f" % (i, ds))

    if verbose:
        print("Calculating reweighted FES..")

    # initialize square array rew_dimension-dimensional
    fes = np.zeros(grid_shape)

    # go through the CV(t) trajectory
    denom = 0.0

    for i, row in enumerate(colvar):
        # build the array of grid indeces locs corresponding to the point closest to current point
        locs = [] * rew_dimension

        for j in range(rew_dimension):
            col = colvar_rew_columns[j]
            val = row[col]
            diff = np.array([abs(gval - val) for gval in s_grid[j]])
            locs.append(diff.argmin())  # find position of minimum in diff array

        locs = tuple(locs)

        # find closest c(t) for this point of time
        indx = int(ceil(float(i) / len(colvar) * num_fes_files)) - 1

        bias = sum([row[j] for j in colvar_bias_columns])
        ebias = exp(bias / kT) / ebetac[indx]
        fes[locs] += ebias
        denom += ebias

    # ignore warnings about log(0) and /0
    np.seterr(all="ignore")

    fes /= denom

    fes = -kT * np.log(fes)

    # set FES minimum to 0
    fes -= np.min(fes)

    return fes, s_grid
