#!/usr/bin/env python3
"""Build Boltz-2 restrained co-fold inputs for the JUDGE POSITIVE CONTROL.

The known KRAS-G12D/HLA-A*11:01 TCRs -- JDI (high-affinity *selective* therapeutic, 7PB2) and
Poole (parental, binds G12D AND WT, 7OW6) -- folded against the 3 scoring states (G12D / WT / empty),
to test whether a restrained static co-fold DIFFERENTIAL (TCR<->peptide ipTM/ipSAE) recovers the
KNOWN selectivity: JDI should show G12D>WT and loaded>empty; Poole should show loaded>empty with a
smaller G12D>WT gap. If even the >4000x-selective JDI shows no detectable static gap, a static
co-fold differential is near-blind here and the campaign must favor differential-AMPLIFYING mechanisms.

Chains:  A=HLA-A*11:01 (full 281 construct), B=b2m, C=peptide (loaded only), D=TCRa, E=TCRb.
Restraint: a single pocket on TCRb(E) to the peptide bulge [C4,C6,C7,C8] (loaded) or the HLA groove
floor (empty), max_distance 8 A -- identical across G12D/WT so the mutation-specificity differential
has ZERO confound (only peptide P6 differs). msa:empty everywhere (symmetric, deterministic, no network).

de-novo rule: the TCR sequences are CONTROLS ONLY (never a design seed).
Assistant-drafted (Claude) 2026-10-27.  Run with any python3 (stdlib only).
"""
import os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TGT = os.path.join(ROOT, "configs/target.yaml")

# HLA + b2m straight from the single source of truth (target.yaml)
_vals = re.findall(r'^\s+sequence:\s*"([A-Z]+)"', open(TGT).read(), re.M)
HLA = next(s for s in _vals if s.startswith("GSHSMRY"))
B2M = next(s for s in _vals if s.startswith("IQRTP"))
G12D, WT = "VVVGADGVGK", "VVVGAGGVGK"
assert len(HLA) == 281 and len(B2M) == 99, (len(HLA), len(B2M))
assert G12D in _vals and WT in _vals, "peptide seqs not found in target.yaml"

# TCR sequences extracted from the crystals (data/pdb/{7PB2,7OW6}.pdb chains D/E). CONTROLS ONLY.
JDI_A = "QKVTQAQTEISVVEKEDVTLDCVYETRDTTYYLFWYKQPPSGELVFLIRRNSFDEQNEISGRYSWNFQKSTSSFNFTITASQVVDSAVYFCALSGPSGAGSYQLTFGKGTKLSVIPNIQNPDPAVYQLRDSKSSDKSVCLFTDFDSDVYITDKCVNSAVAWSN"
JDI_B = "NAGVTQTPKFRVLKTGQSMTLLCAQDMNHEYMYWYRQDPGMGLRLIHYSVGEGTTAKGEVPDGYNVSRLKKQNFLLGLESAAPSQTSVYFCASSYGPGQHNSPLHFGNGTRLTVTEDLNKVFPPEVAVFEPSEAEISHTQKATLVCLATGFYPDHVELSWWVNGKEVHSGVCTDPQPLKEQPALNDSRYALSSRLRVSATFWQDPRNHFRCQVQFYGLSENDEWTQDRAKPVTQIVSAEAWGRA"
POOLE_A = "AQKVTQAQTEISVVEKEDVTLDCVYETRDTAYYLFWYKQPPSGELVFLIRQPWWGEQNEISGRYSWNFQKSTSSFNFTITASQVVDSAVYFCAMSVPSGDGSYQFTFGKGTKLSVIPNIQNPDPAVYQLRDSKSSDKSVCLFTDFDSQTNVSSDVYITDKCVLKSNSAVAWSNKACANAFN"
POOLE_B = "MNAGVTQTPKFRVLKTGQSMTLLCAQDMNHEYMYWYRQDPGMGLRLIHYSVGEGTTAKGEVPDGYNVSRLKKQNFLLGLESAAPSQTSVYFCASKVGPGQHNSPLHFGNGTRLTVTEDLNKVFPPEVAVFEPSEAEISHTQKATLVCLATGFYPDHVELSWWVNGKEVHSGVCTDPQPLKEQPALNDSRYALSSRLRVSATFWQDPRNHFRCQVQFYGLSENDEWTQDRAKPVTQIVSAEAWGRA"

def prot(cid, seq):
    return f"  - protein:\n      id: {cid}\n      sequence: {seq}\n      msa: empty\n"

def yaml_for(pepseq, tcr_a, tcr_b):
    s = "version: 1\nsequences:\n" + prot("A", HLA) + prot("B", B2M)
    if pepseq:
        s += prot("C", pepseq)
    s += prot("D", tcr_a) + prot("E", tcr_b)
    contacts = "[[C, 4], [C, 6], [C, 7], [C, 8]]" if pepseq else "[[A, 66], [A, 69], [A, 146], [A, 150], [A, 155]]"
    s += f"constraints:\n  - pocket:\n      binder: E\n      contacts: {contacts}\n      max_distance: 8.0\n"
    return s

OUT = os.path.join(ROOT, "folds/poscontrol/yaml")
os.makedirs(OUT, exist_ok=True)
jobs = {
    "jdi_g12d":   (G12D, JDI_A, JDI_B),
    "jdi_wt":     (WT,   JDI_A, JDI_B),
    "jdi_empty":  (None, JDI_A, JDI_B),
    "poole_g12d": (G12D, POOLE_A, POOLE_B),
    "poole_wt":   (WT,   POOLE_A, POOLE_B),
}
for nm, (pep, a, b) in jobs.items():
    open(os.path.join(OUT, f"{nm}.yaml"), "w").write(yaml_for(pep, a, b))
    print(f"wrote {nm:12s} chains A,B,{'C,' if pep else ''}D,E  pep={pep}")
print("OUT", OUT)
