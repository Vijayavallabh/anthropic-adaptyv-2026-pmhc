#!/usr/bin/env python
"""Build solvated Amber system (ff14SB + TIP3P, 150 mM NaCl) for a TCR:pMHC complex.
Two-pass tleap: (1) solvate+report charge/waters, (2) add neutralizing + 150 mM ions.
Usage: python -I build_md.py <tag> <clean_pdb> <ss 'a-b,c-d,...'> <outdir>
"""
import sys, os, re, subprocess, math

tag, pdb, ss, outdir = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
pdb = os.path.abspath(pdb)
outdir = os.path.abspath(outdir)
os.makedirs(outdir, exist_ok=True)
pairs = [p.split('-') for p in ss.split(',')] if ss else []
# Disulfides are carried as CONECT records in the pdb4amber clean PDB and are
# auto-bonded by tleap on loadpdb; explicit bond cmds would duplicate -> fatal.
bonds = f"# {len(pairs)} disulfides via CONECT records (no explicit bond cmds)"
AMBERHOME = "/home/prachh/miniconda3/envs/ambertools"
TLEAP = f"{AMBERHOME}/bin/tleap"
ENV = dict(os.environ, AMBERHOME=AMBERHOME, PATH=f"{AMBERHOME}/bin:"+os.environ.get("PATH",""))
def run_tleap(infile):
    return subprocess.run([TLEAP,"-f",os.path.basename(infile)], cwd=outdir,
                          capture_output=True, text=True, env=ENV)

# ---- Pass 1: solvate + neutralize only, report net charge & water count ----
s1 = f"""source leaprc.protein.ff14SB
source leaprc.water.tip3p
mol = loadpdb {pdb}
{bonds}
charge mol
solvateoct mol TIP3PBOX 10.0
charge mol
quit
"""
p1 = os.path.join(outdir, f"{tag}_leap1.in")
open(p1,'w').write(s1)
log1 = run_tleap(p1)
txt = log1.stdout + log1.stderr
# first 'charge' (solute) then after solvate second charge (same solute charge)
charges = re.findall(r"Total (?:unperturbed|perturbed) charge:\s*([-\d.]+)", txt)
# count waters added
mwat = re.search(r"Added (\d+) residues", txt)
# robust water count: count WAT in the volume via 'solvateoct' report
nwat = None
m2 = re.findall(r"Added (\d+) residues", txt)
if m2: nwat = int(m2[-1])
print(f"[{tag}] charges seen: {charges}, waters: {nwat}")
if not charges or nwat is None:
    print("---- leap1 tail ----"); print(txt[-3000:]); sys.exit("Pass1 parse failed")
Q = float(charges[0])
nQ = int(round(Q))
# 150 mM: n_pairs = 0.15 mol/L * (nwat / 55.56 mol/L)
npair = int(round(0.15 * nwat / 55.56))
nNa, nCl = npair, npair
if nQ > 0:   nCl += nQ      # positive solute -> extra Cl to neutralize
elif nQ < 0: nNa += -nQ     # negative solute -> extra Na
print(f"[{tag}] net charge={Q} (round {nQ}); waters={nwat}; 150mM pairs={npair}; add Na+={nNa} Cl-={nCl}")

# ---- Pass 2: rebuild, add exact ion counts, save ----
s2 = f"""source leaprc.protein.ff14SB
source leaprc.water.tip3p
mol = loadpdb {pdb}
{bonds}
solvateoct mol TIP3PBOX 10.0
addionsrand mol Na+ {nNa} Cl- {nCl}
charge mol
saveamberparm mol {tag}_solv.prmtop {tag}_solv.inpcrd
savepdb mol {tag}_solv.pdb
quit
"""
p2 = os.path.join(outdir, f"{tag}_leap2.in")
open(p2,'w').write(s2)
log2 = run_tleap(p2)
txt2 = log2.stdout + log2.stderr
fin = re.findall(r"Total (?:unperturbed|perturbed) charge:\s*([-\d.]+)", txt2)
print(f"[{tag}] final system charge: {fin[-1] if fin else '??'}")
prm = os.path.join(outdir, f"{tag}_solv.prmtop")
if (not os.path.exists(prm)) or os.path.getsize(prm) == 0:
    print("---- leap2 tail ----"); print(txt2[-3500:]); sys.exit("Pass2 saveamberparm failed (empty/missing prmtop)")
# atom count
natom = None
with open(prm) as fh:
    for i,ln in enumerate(fh):
        if ln.startswith("%FLAG POINTERS"):
            fh.readline(); vals=fh.readline().split(); natom=int(vals[0]); break
print(f"[{tag}] BUILD OK -> {prm}  natoms={natom}")
