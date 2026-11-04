#!/usr/bin/env python3
"""Free peptide-MHC ensemble inputs (NO binder): fold HLA+b2m+peptide many times to probe whether the
P4-P7 bulge is FLOPPIER for WT (Gly6) than G12D (Asp6). That conformational ordering difference is the
UNBOUND free-energy term the positive control proved static co-fold is blind to, and it sets the
intrinsic selectivity ceiling for every shape-gripping (conformation-gated/selector) design.

A cheap first look via Boltz diffusion-sample spread (orthogonal, idle-GPU); escalate to explicit MD if
the signal is real-but-marginal or if Boltz locks both into the canonical bulge (no spread = proxy blind).
msa:empty, no restraint (HLA anchors P2/P10; analysis filters to well-anchored poses). stdlib only.
"""
import os, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
v = re.findall(r'^\s+sequence:\s*"([A-Z]+)"', open(os.path.join(ROOT, "configs/target.yaml")).read(), re.M)
HLA = next(s for s in v if s.startswith("GSHSMRY"))
B2M = next(s for s in v if s.startswith("IQRTP"))
def prot(c, s): return f"  - protein:\n      id: {c}\n      sequence: {s}\n      msa: empty\n"
def yml(pep): return "version: 1\nsequences:\n" + prot("A", HLA) + prot("B", B2M) + prot("C", pep)
OUT = os.path.join(ROOT, "folds/free_ens/yaml"); os.makedirs(OUT, exist_ok=True)
for nm, pep in [("free_g12d", "VVVGADGVGK"), ("free_wt", "VVVGAGGVGK")]:
    open(os.path.join(OUT, f"{nm}.yaml"), "w").write(yml(pep)); print("wrote", nm, pep)
print("OUT", OUT)
