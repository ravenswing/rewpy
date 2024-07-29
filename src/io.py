import pandas as pd
import numpy as np
from pathlib import Path


def find_fes_files(fes_prefix: str) -> list:
    path = Path(fes_prefix)
    # Extract the numbers of the fes files present, with the allocated name.
    fes_numbers = [
        str(a.stem).split(str(path.name))[-1]
        for a in path.parent.rglob(str(path.name) + "*")
    ]
    # Check that all the fes files found fit the naming convention, and numbers can be parsed as int.
    assert all(
        [s.isdigit() for s in fes_numbers]
    ), "Some FES filenames do not conform to the required numbering of <pref><num>.dat"
    # Convert the file numbers to integers and extract the max and min number.
    fes_numbers = np.asarray([int(s) for s in fes_numbers])
    fes_start: int = fes_numbers.min()
    fes_end: int = fes_numbers.max()
    # Generate list of expected paths, with contiunous numbering and correct names.
    fes_paths = [
        path.with_name(f"{path.name}{i}.dat") for i in np.arange(fes_start, fes_end + 1)
    ]
    # Check that all of the paths exist and can be read.
    assert all(
        [p.is_file() for p in fes_paths]
    ), f"Some FES files are incorrectly named or missing, expected continuous numbering from {fes_paths[0]} to {fes_paths[-1]}"
    # Return correct, ordered, readable list of paths.
    return fes_paths


def load_fes(path) -> pd.DataFrame:
    # Read in the header line of the FES file.
    with open(path) as f:
        header = f.readlines()[0].split()
    # Sum_hills FES contain FIELDS line, so simply extract the column names.
    assert header[0] == "#!", "Header not found in FES file, cannot read column names"
    fields = header[2:]
    # Standardise column naming (dependends sum_hills run with 1 or 2 CVs)
    fields = [f.replace("projection", "free") for f in fields]
    fields = [f.replace("file.free", "free") for f in fields]
    # If needed... Extract CV names - all column names before the free energy.
    # cvs = fields[: fields.index("free")]
    fes = pd.read_csv(path, sep="\s+", names=fields, comment="#")

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
