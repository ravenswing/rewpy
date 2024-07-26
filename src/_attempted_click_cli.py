# config.py

import click


@click.command()
@click.argument(
    "fes",
    type=click.File(mode="r"),
)
@click.argument(
    "colvar",
    type=click.File(mode="r"),
)
@click.option(
    "-o",
    "--output",
    type=click.STRING,
    default="fes.dat",
    help="Name of reweighted FES file.",
)
@click.option(
    "-k",
    "--kT",
    type=click.FLOAT,
    default=2.49,
    help="kT in the energy units of the FES files",
)
@click.option(
    "-y",
    "--bias-factor",
    type=click.FLOAT,
    default=10,
    help="biasfactor used in the well-tempered metadynamics, if omitted assumes a non-well-tempered metadynamics",
)
@click.option(
    "--num-fes",
    type=click.INT,
    default=100,
    help="kT in the energy units of the FES files",
)
@click.option(
    "--fes-col",
    type=click.INT,
    default=3,
    help="kT in the energy units of the FES files",
)
@click.option(
    "--colvar-bias-col",
    nargs=-1,
    type=click.INT,
    default=2,
    help="kT in the energy units of the FES files",
)
@click.option(
    "--colvar-rew-col",
    nargs=-1,
    type=click.INT,
    default=3,
    help="kT in the energy units of the FES files",
)
@click.option(
    "--exp-bct-file",
    type=click.STRING,
    help="Name of reweighted FES file.",
)
@click.option(
    "--exp-bct-out",
    type=click.STRING,
    default="rew_exp_bct.dat",
    help="Name of reweighted FES file.",
)
@click.option("-v", "--verbose", is_flag=True)
def cli():
    pass
