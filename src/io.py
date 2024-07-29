import pandas as pd
from glob import glob


def find_fes_files(fes_prefix: str):
    print(fes_prefix)


def load_fes(filename: str) -> pd.DataFrame:
    # Read in the header line of the FES file.
    with open(filename) as f:
        header = f.readlines()[0].split()
    # Sum_hills FES contain FIELDS line, so simply extract the column names.
    assert header[0] == "#!", "Header not found in FES file, cannot read column names"
    fields = header[2:]
    # Standardise column naming (dependends sum_hills run with 1 or 2 CVs)
    fields = [f.replace("projection", "free") for f in fields]
    fields = [f.replace("file.free", "free") for f in fields]
    # If needed... Extract CV names - all column names before the free energy.
    # cvs = fields[: fields.index("free")]
    fes = pd.read_csv(filename, sep="\s+", names=fields, comment="#")

    return fes


# Load colvar
def load_colvar(filename: str):
    with open(filename) as f:
        fields = f.readlines()[0].split()[2:]
    # Read in old COLVAR file into DataFrame.
    # Filters out comment lines and splits columns via whitespace.
    colvar = pd.concat(
        [
            df
            for df in pd.read_csv(
                filename,
                sep="\s+",
                names=fields,
                skiprows=1,
                comment="#",
                chunksize=1000,
            )
        ]
    )
    # Round the timestamps to ensure successful merging
    colvar["int_time"] = colvar["time"].astype(float).astype(int)
    # Remove duplicate lines created by restarts
    colvar = colvar.drop_duplicates(subset="int_time", keep="last")
    colvar = colvar.reset_index(drop=True)

    return colvar


# OUTPUT RESULTS TO FILE
def save_output(output_file, rew_dimension, s_grid, fes, verbose) -> None:
    if verbose:
        print("Saving results on %s" % output_file)

    # save the FES in the format: FES(x,y) (one increment of y per row)
    # np.savetxt('fes_rew_matlabfmt.dat', fes, fmt='%.8e', delimiter=' ')

    # print the FES in the format:
    # x,y,z,FES(x,y,z) for 3D
    # x,y,FES(x,y) for 2D
    # x,FES(x) for 1D
    with open(output_file, "w") as f:
        if rew_dimension == 3:
            for nz, z in enumerate(s_grid[2]):
                for ny, y in enumerate(s_grid[1]):
                    for nx, x in enumerate(s_grid[0]):
                        f.write(
                            "%20.12f %20.12f %20.12f %20.12f\n"
                            % (x, y, z, fes[nx][ny][nz])
                        )
                    f.write("\n")
        elif rew_dimension == 2:
            for ny, y in enumerate(s_grid[1]):
                for nx, x in enumerate(s_grid[0]):
                    f.write("%20.12f %20.12f %20.12f\n" % (x, y, fes[nx][ny]))
                f.write("\n")
        elif rew_dimension == 1:
            for nx, x in enumerate(s_grid[0]):
                f.write("%20.12f %20.12f\n" % (x, fes[nx]))
    f.close()
