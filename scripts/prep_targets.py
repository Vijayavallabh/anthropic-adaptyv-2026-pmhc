#!/usr/bin/env python
"""Target prep for the KRAS G12D / HLA-A*11:01 pMHC challenge.

From the raw crystal structures, build the clean scoring states every design strategy
and the judge pipeline need:
  g12d.pdb        chains A/B/C = HLA / b2m / peptide VVVGADGVGK  (ORDERED design-target conf, from 7OW6)
  wt_insilico.pdb same as g12d but peptide P6 ASP->GLY (isolates the single-residue difference)
  empty.pdb       chains A/B   = HLA / b2m, peptide removed      (peptide-free HLA negative state)
  wt_crystal.pdb  chains A/B/C from 7OW5 (independent WT crystal, cross-check)

Plus manifest.json: chain map, peptide register, P6 resseq, binder-readable hotspots
(P7 backbone apex, P8 Val side chain, P4 backbone -- from the SASA analysis; NOT P6, buried),
and the resolved HLA/b2m sequences. TCR, waters, ions, ligands, and alt-loc B+ are dropped.

Assistant-drafted (Claude) for anthropic-adaptyv-2026-pmhc, 2026-10-27.
Run:  /home/prachh/miniconda3/envs/ambertools/bin/python -I scripts/prep_targets.py
"""
import json, os
from Bio.PDB import PDBParser, PDBIO, Select

PDBDIR = "data/pdb"
OUT = "data/targets"
BACKBONE = {"N", "CA", "C", "O"}
STD = {"ALA","ARG","ASN","ASP","CYS","GLN","GLU","GLY","HIS","ILE","LEU","LYS",
       "MET","PHE","PRO","SER","THR","TRP","TYR","VAL"}
_3to1 = {"ALA":"A","ARG":"R","ASN":"N","ASP":"D","CYS":"C","GLN":"Q","GLU":"E","GLY":"G","HIS":"H",
         "ILE":"I","LEU":"L","LYS":"K","MET":"M","PHE":"F","PRO":"P","SER":"S","THR":"T","TRP":"W",
         "TYR":"Y","VAL":"V"}

def model_of(path):
    return PDBParser(QUIET=True).get_structure("s", path)[0]

def inventory(model):
    inv = {}
    for ch in model:
        res = [r for r in ch if r.id[0] == " " and r.resname in STD]
        inv[ch.id] = {"n": len(res),
                      "seq": "".join(_3to1.get(r.resname, "X") for r in res),
                      "resseqs": [r.id[1] for r in res]}
    return inv

def identify(inv):
    pep = [c for c, d in inv.items() if d["n"] <= 12 and d["seq"].startswith("VVVGA")]
    pep_id = pep[0] if pep else None
    nonpep = {c: d for c, d in inv.items() if c != pep_id}
    hla_id = max(nonpep, key=lambda c: nonpep[c]["n"]) if nonpep else None
    b2m = {c: d for c, d in nonpep.items() if c != hla_id and 90 <= d["n"] <= 112}
    b2m_id = min(b2m, key=lambda c: abs(b2m[c]["n"] - 99)) if b2m else None
    return hla_id, b2m_id, pep_id

class Keep(Select):
    def __init__(self, chains): self.chains = set(chains)
    def accept_chain(self, ch): return 1 if ch.id in self.chains else 0
    def accept_residue(self, r): return 1 if (r.id[0] == " " and r.resname in STD) else 0
    def accept_atom(self, a): return 1 if a.get_altloc() in (" ", "A") else 0

def write(model, chains, path):
    io = PDBIO(); io.set_structure(model); io.save(path, Keep(chains))

os.makedirs(OUT, exist_ok=True)
manifest = {"provenance": "7OW6 (G12D ordered) + 7OW5 (WT crystal); TCR/waters/ions/altloc-B+ dropped"}

# --- 7OW6 -> g12d, empty, wt_insilico ---
m6 = model_of(f"{PDBDIR}/7OW6.pdb")
inv6 = inventory(m6)
hla, b2m, pep = identify(inv6)
assert (hla, b2m, pep) == ("A", "B", "C"), f"7OW6 chains unexpected: {(hla, b2m, pep)}"
assert inv6[pep]["seq"] == "VVVGADGVGK", inv6[pep]["seq"]
write(m6, [hla, b2m, pep], f"{OUT}/g12d.pdb")
write(m6, [hla, b2m],      f"{OUT}/empty.pdb")

# wt_insilico: reparse the clean g12d (altlocs resolved), mutate C/6 ASP->GLY in place
mg = model_of(f"{OUT}/g12d.pdb")
r6 = mg[pep][(" ", 6, " ")]
assert r6.resname == "ASP", r6.resname
for an in [a.name for a in list(r6)]:
    if an not in BACKBONE:
        r6.detach_child(an)
r6.resname = "GLY"
wtseq = "".join(_3to1.get(r.resname, "X") for r in mg[pep] if r.id[0] == " ")
assert wtseq == "VVVGAGGVGK", wtseq
io = PDBIO(); io.set_structure(mg); io.save(f"{OUT}/wt_insilico.pdb")

# --- 7OW5 -> wt_crystal (independent WT reference) ---
m5 = model_of(f"{PDBDIR}/7OW5.pdb")
inv5 = inventory(m5)
h5, b5, p5 = identify(inv5)
if h5 and b5 and p5:
    write(m5, [h5, b5, p5], f"{OUT}/wt_crystal.pdb")
manifest["wt_crystal_chains"] = {"hla": h5, "b2m": b5, "pep": p5,
                                 "pep_seq": inv5[p5]["seq"] if p5 else None}

manifest["states"] = {
    "g12d":        {"file": "g12d.pdb", "chains": {"hla": "A", "b2m": "B", "pep": "C"}, "pep_seq": "VVVGADGVGK"},
    "wt_insilico": {"file": "wt_insilico.pdb", "pep_seq": "VVVGAGGVGK",
                    "note": "WT seq in the mutant's ORDERED backbone (C/6 ASP->GLY). HARD negative for "
                            "ELECTROSTATIC/direct designs only; BIASED (false-non-selective) for CONFORMATIONAL "
                            "designs -> use the floppy WT ensemble for those. See wt_negative_policy."},
    "empty":       {"file": "empty.pdb", "chains": {"hla": "A", "b2m": "B"}, "pep_seq": None},
    "wt_crystal":  {"file": "wt_crystal.pdb", "note": "independent WT crystal 7OW5"},
}
manifest["peptide_register"] = {"chain": "C", "resseqs": list(range(1, 11)),
                                "discriminating": {"pos": 6, "resseq": 6, "g12d": "ASP", "wt": "GLY"}}
# binder-readable hotspots from notes/epitope_7OW6.json (NOT P6: buried/inward)
manifest["binder_hotspots"] = [
    {"pos": 7, "resseq": 7, "res": "GLY", "feature": "backbone apex of up-bulge", "sc_sasa": 0.0, "total_sasa": 74.1, "note": "MOST exposed; read main-chain"},
    {"pos": 8, "resseq": 8, "res": "VAL", "feature": "most exposed side chain", "sc_sasa": 37.2, "total_sasa": 45.1, "note": "hydrophobic anchor"},
    {"pos": 4, "resseq": 4, "res": "GLY", "feature": "backbone bulge", "sc_sasa": 0.0, "total_sasa": 35.3},
    {"pos": 5, "resseq": 5, "res": "ALA", "feature": "partial; native TCR reads it", "sc_sasa": 8.9, "total_sasa": 29.3},
    {"pos": 6, "resseq": 6, "res": "ASP", "feature": "DISCRIMINATOR but semi-buried/inward", "sc_sasa": 8.3, "total_sasa": 20.0, "note": "do NOT target directly; read via bulge geometry + electrostatics"},
]
manifest["resolved_seqs"] = {"hla_A": inv6["A"]["seq"], "b2m_B": inv6["B"]["seq"]}
# The WT negative is NOT a single structure: discrimination is largely an UNBOUND conformational
# free-energy difference (WT Gly6 -> floppy bulge; G12D Asp6 -> locked; 7OW4: free bulge disorders)
# that single-pose scoring cannot see. Apply the right WT negative per design mechanism.
manifest["wt_negative_policy"] = {
    "ordered_chemistry_negative": "wt_insilico.pdb -- WT seq in the mutant ORDERED backbone; the HARD "
        "negative for ELECTROSTATIC/direct-readout designs (shape identical, only P6 chemistry differs). "
        "NEVER the negative for CONFORMATIONAL designs: they SHOULD grip the ordered shape, so frozen-ordered "
        "WT reads as false-non-selective -> false reject.",
    "conformational_negative": "WT free-peptide-MHC MD ENSEMBLE (TO BUILD) = the floppy states, plus an "
        "unbound ordering-penalty term ddG_order(WT vs G12D). The correct negative for CONFORMATIONAL/gated designs.",
    "cofold_from_seq": "Boltz/Chai fold WT from SEQUENCE (not from wt_insilico.pdb) -> one pose, likely "
        "ordered-bulge-like -> UNDER-captures WT floppiness; treat as complementarity-only.",
    "rule": "Score each design's g12d-wt gap against the HARDEST WT negative applicable to its mechanism; "
        "a maximally-robust design clears ALL (ordered-chemistry AND floppy-ensemble).",
}
json.dump(manifest, open(f"{OUT}/manifest.json", "w"), indent=2)

print("WROTE", OUT)
for f in sorted(os.listdir(OUT)):
    print("   ", f, os.path.getsize(f"{OUT}/{f}"), "B")
print("g12d pep:", inv6["C"]["seq"], " wt_insilico pep:", wtseq,
      " wt_crystal pep:", inv5[p5]["seq"] if p5 else "NA")
print("HLA resolved:", inv6["A"]["n"], "aa   b2m resolved:", inv6["B"]["n"], "aa")
