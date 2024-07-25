# RewPy - Metadynamics Reweighting in Python

---
## Mode 1: Tiwary
### Time-independent Free Energy reconstruction script (a.k.a. reweight)
based on the algorithm proposed by Tiwary and Parrinello JPCB 2014

Typical usage:

1. to project your metadynamics FES on CVs you did not bias during your metadynamics run
2. to estimate the error on your FE profiles by comparing them with the FE profiles obtained integrating the metadynamics bias e.g. using plumed sum_hills

### Example:
```shell
reweight.py -bsf 5.0 -kt 2.5 -fpref fes2d- -nf 80 -fcol 3 -colvar COLVAR -biascol 4 -rewcol 2 3
```
Takes as input 80 FES files: fes2d-0.dat, fes2d-1.dat, ... fes2d-79.dat obtained using a well-tempered
metadynamics with bias factor 5 and containing the free energy in the 3rd column and the COLVAR file
containing the bias in the 4th column and outputs the FES projected on the CVs in column 2 and 3 of COLVAR file.

---
## Mode 2

---
## Acknowledgements

Ludovico Sutto (l.sutto@ucl.ac.uk) - v1.0 - c. April 2015
Ladislav Hovan (ladislav.hovan.15@ucl.ac.uk) - v2.0 - c. January 2019

---
