#!/usr/bin/env python
"""Self-consistent single-trajectory MM-GBSA in OpenMM (GBn2, 150 mM, NoCutoff, no PBC).
dG_bind = E(complex) - E(receptor) - E(ligand); pMHC(ligand)=first NLIG atoms, TCR(receptor)=rest.
Reads a DRY, WHOLE complex NetCDF trajectory (cpptraj: strip solvent + autoimage).
Usage: python -I score_gbsa.py <com.parm7> <rec.parm7> <lig.parm7> <nlig> <stride> <plat> <out.csv> <nc...>"""
import sys, numpy as np, csv
from scipy.io import netcdf_file
from openmm.app import AmberPrmtopFile, GBn2, NoCutoff
from openmm import Context, VerletIntegrator, Platform, unit

com_prm, rec_prm, lig_prm = sys.argv[1:4]
nlig = int(sys.argv[4]); stride = int(sys.argv[5]); plat = sys.argv[6]; outcsv = sys.argv[7]
ncs = sys.argv[8:]
KCAL = unit.kilocalorie_per_mole

def mk(p):
    s=AmberPrmtopFile(p).createSystem(implicitSolvent=GBn2, implicitSolventSaltConc=0.15*unit.molar,
        nonbondedMethod=NoCutoff, soluteDielectric=1.0, solventDielectric=78.5)
    try: pf=Platform.getPlatformByName(plat)
    except Exception: pf=Platform.getPlatformByName("CPU")
    return Context(s, VerletIntegrator(1.0*unit.femtosecond), pf), AmberPrmtopFile(p).topology.getNumAtoms()

ctx_com,nc_=mk(com_prm); ctx_rec,nr_=mk(rec_prm); ctx_lig,nl_=mk(lig_prm)
assert nl_==nlig and nc_==nlig+nr_, f"atom mismatch com{nc_} lig{nl_} rec{nr_} nlig{nlig}"
def E(ctx,a): ctx.setPositions(unit.Quantity(np.asarray(a,dtype=float),unit.nanometer)); \
              return ctx.getState(getEnergy=True).getPotentialEnergy().value_in_unit(KCAL)

rows=[]
for ncf in ncs:
    f=netcdf_file(ncf,'r',mmap=False)
    C=f.variables['coordinates'][:]   # (nframe,natom,3) Angstrom
    f.close()
    nf=C.shape[0]
    print(f"{ncf}: {nf} frames, {C.shape[1]} atoms (stride {stride})")
    for fi in range(0,nf,stride):
        pos=C[fi]/10.0   # A->nm
        ec=E(ctx_com,pos); er=E(ctx_rec,pos[nlig:]); el=E(ctx_lig,pos[:nlig])
        rows.append((ncf,fi,ec,er,el,ec-er-el))
with open(outcsv,"w",newline="") as fh:
    w=csv.writer(fh); w.writerow(["traj","frame","E_com","E_rec","E_lig","dG_bind"]); w.writerows(rows)
dG=np.array([r[5] for r in rows])
print(f"TOTAL frames={len(dG)}  dG_bind mean={dG.mean():.2f} std={dG.std():.2f} sem={dG.std()/len(dG)**0.5:.2f} range[{dG.min():.1f},{dG.max():.1f}]")
