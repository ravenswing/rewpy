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
