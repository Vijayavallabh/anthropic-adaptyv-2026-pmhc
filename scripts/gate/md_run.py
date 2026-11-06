#!/usr/bin/env python
"""Explicit-solvent MD (OpenMM, CUDA) for a solvated Amber system.
ff14SB/TIP3P prmtop; HMR 4 fs; minimize -> NVT -> NPT equil -> NPT production.
Writes DCD (every 10 ps) + final state. Protein heavy-atom restraints during equil.
Usage: python -I md_run.py <prmtop> <inpcrd> <outprefix> <prod_ns> <seed>
Env: CUDA_VISIBLE_DEVICES set by caller (one GPU). OMP threads capped by caller.
"""
import sys, time
from openmm import (LangevinMiddleIntegrator, MonteCarloBarostat, Platform,
                    CustomExternalForce, unit)
from openmm.app import (AmberPrmtopFile, AmberInpcrdFile, Simulation, PME,
                        HBonds, DCDReporter, StateDataReporter, CheckpointReporter)

prmtop_f, inpcrd_f, outpref, prod_ns, seed = sys.argv[1:6]
prod_ns = float(prod_ns); seed = int(seed)
T = 300.0*unit.kelvin
dt = 0.004*unit.picoseconds            # 4 fs with HMR
kcal = unit.kilocalorie_per_mole/unit.angstrom**2

prm = AmberPrmtopFile(prmtop_f)
crd = AmberInpcrdFile(inpcrd_f)
system = prm.createSystem(nonbondedMethod=PME, nonbondedCutoff=1.0*unit.nanometer,
                          constraints=HBonds, rigidWater=True,
                          hydrogenMass=1.5*unit.amu)

# --- positional restraint force (protein heavy atoms) ---
rest = CustomExternalForce("k*periodicdistance(x,y,z,x0,y0,z0)^2")
rest.addGlobalParameter("k", 0.0)
for p in ("x0","y0","z0"): rest.addPerParticleParameter(p)
prot_heavy = []
for atom in prm.topology.atoms():
    res = atom.residue.name
    if res in ("WAT","HOH","Na+","Cl-","NA","CL"): continue
    if atom.element is not None and atom.element.symbol == "H": continue
    rest.addParticle(atom.index, crd.positions[atom.index].value_in_unit(unit.nanometer))
    prot_heavy.append(atom.index)
system.addForce(rest)

integrator = LangevinMiddleIntegrator(T, 1.0/unit.picosecond, dt)
integrator.setRandomNumberSeed(seed)
platform = Platform.getPlatformByName("CUDA")
props = {"Precision":"mixed","DeterministicForces":"false"}
sim = Simulation(prm.topology, system, integrator, platform, props)
sim.context.setPositions(crd.positions)
if crd.boxVectors is not None:
    sim.context.setPeriodicBoxVectors(*crd.boxVectors)

def set_k(kc):  # kcal/mol/A^2 -> internal
    sim.context.setParameter("k", (kc*kcal).value_in_unit(unit.kilojoule_per_mole/unit.nanometer**2))

log = open(outpref+"_md.log","w")
def say(*a):
    m=" ".join(str(x) for x in a); print(m); log.write(m+"\n"); log.flush()

t0=time.time()
say(f"[{outpref}] atoms={system.getNumParticles()} prot_heavy={len(prot_heavy)} seed={seed} prod_ns={prod_ns}")
say(f"[{outpref}] platform={platform.getName()} dev={platform.getPropertyValue(sim.context,'DeviceIndex') if False else 'env'}")

# 1) Minimize restrained then free
set_k(10.0); sim.minimizeEnergy(maxIterations=8000); say(f"[{outpref}] min restrained done {time.time()-t0:.0f}s")
set_k(0.0);  sim.minimizeEnergy(maxIterations=5000); say(f"[{outpref}] min free done {time.time()-t0:.0f}s")

# 2) NVT 100 ps restrained (heavy restraint)
set_k(5.0)
sim.context.setVelocitiesToTemperature(T, seed)
sim.step(25000); say(f"[{outpref}] NVT 100ps done {time.time()-t0:.0f}s")

# 3) NPT 200 ps restrained (backbone-ish via reduced k) + barostat
baro = MonteCarloBarostat(1.0*unit.bar, T, 100); baro_idx=system.addForce(baro)
sim.context.reinitialize(preserveState=True)
set_k(2.0); sim.step(50000); say(f"[{outpref}] NPT restrained 200ps done {time.time()-t0:.0f}s")

# 4) NPT 200 ps free (release restraints, equilibrate density)
set_k(0.0); sim.step(50000); say(f"[{outpref}] NPT free 200ps done {time.time()-t0:.0f}s")

# 5) Production NPT free
nprod = int(round(prod_ns*1000/0.004))  # steps (4 fs)
save_every = int(round(10/0.004))       # 10 ps
sim.reporters.append(DCDReporter(outpref+"_prod.dcd", save_every))
sim.reporters.append(StateDataReporter(outpref+"_prod.csv", save_every, step=True,
      time=True, potentialEnergy=True, temperature=True, density=True, speed=True, elapsedTime=True))
sim.reporters.append(CheckpointReporter(outpref+"_prod.chk", save_every*10))
say(f"[{outpref}] PRODUCTION start: {nprod} steps, save every {save_every} ({prod_ns} ns)")
sim.step(nprod)
# save final
from openmm.app import PDBFile
st=sim.context.getState(getPositions=True)
say(f"[{outpref}] PRODUCTION done total {time.time()-t0:.0f}s  -> {outpref}_prod.dcd")
log.close()
