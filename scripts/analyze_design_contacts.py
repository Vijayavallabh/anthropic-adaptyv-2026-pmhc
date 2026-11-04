#!/usr/bin/env python3
"""Peptide-centricity gate for pMHC binder designs. For each design (binder + pMHC), report the fraction
of binder heavy-atom contacts (<5A) landing on the PEPTIDE vs the HLA a1/a2 HELICES vs the rest of HLA.
Want f_pep high and f_helix LOW (helix-reading -> empty-MHC / pan-peptide binder = the dominant failure).
Chains classified by sequence (HLA starts GSHSMRY, b2m IQRTP, peptide VVVGA); binder = the remainder.
Usage: analyze_design_contacts.py <cif_or_pdb> ...   Run with ambertools py (Bio)."""
import sys
from collections import defaultdict
from Bio.PDB import MMCIFParser, PDBParser, NeighborSearch
_3 = {"ALA":"A","ARG":"R","ASN":"N","ASP":"D","CYS":"C","GLN":"Q","GLU":"E","GLY":"G","HIS":"H",
      "ILE":"I","LEU":"L","LYS":"K","MET":"M","PHE":"F","PRO":"P","SER":"S","THR":"T","TRP":"W","TYR":"Y","VAL":"V"}
HELIX = set(range(57, 86)) | set(range(138, 181))  # HLA-A a1/a2 helices (groove walls)

def seq(res): return "".join(_3.get(r.resname, "X") for r in res)

def classify(chains):
    pep = hla = b2m = binder = None
    info = {cid: seq(res) for cid, res in chains.items()}
    for cid, s in info.items():
        if s.startswith("GSHSMRY"): hla = cid
        elif s.startswith("IQRTP"): b2m = cid
        elif s.startswith("VVVGA") and len(s) <= 12: pep = cid
    for cid in chains:
        if cid not in (hla, b2m, pep): binder = cid
    return hla, b2m, pep, binder

def analyze(path):
    P = MMCIFParser(QUIET=True) if path.endswith(".cif") else PDBParser(QUIET=True)
    m = P.get_structure("s", path)[0]
    chains = {c.id: [r for r in c if r.id[0] == " "] for c in m}
    hla, b2m, pep, binder = classify(chains)
    if not (hla and pep and binder):
        return dict(path=path, err=f"classify failed hla={hla} pep={pep} binder={binder} chains={{k:len(v) for k,v in chains.items()}}")
    tgt_atoms = [a for cid in (hla, b2m, pep) if cid for r in chains[cid] for a in r]
    ns = NeighborSearch(tgt_atoms)
    contacts = defaultdict(int)
    for r in chains[binder]:
        for a in r:
            for nb in ns.search(a.coord, 5.0):
                pr = nb.get_parent(); cid = pr.get_parent().id
                contacts[(cid, pr.id[1])] += 1
    tot = sum(contacts.values()) or 1
    pep_c = sum(v for (c, ri), v in contacts.items() if c == pep)
    hla_c = sum(v for (c, ri), v in contacts.items() if c == hla)
    helix_c = sum(v for (c, ri), v in contacts.items() if c == hla and ri in HELIX)
    pep_res = sorted({ri for (c, ri), v in contacts.items() if c == pep})
    return dict(path=path.split("/")[-1], binder_len=len(chains[binder]), n_contact=tot,
                f_pep=round(pep_c / tot, 2), f_hla=round(hla_c / tot, 2), f_helix=round(helix_c / tot, 2),
                pep_res=pep_res)

if __name__ == "__main__":
    print(f"{'design':28s} {'blen':>4} {'ncon':>5} {'f_pep':>5} {'f_hla':>5} {'f_helix':>7}  pep_res_contacted")
    good = 0
    for p in sys.argv[1:]:
        r = analyze(p)
        if r.get("err"): print(f"{r['path'][:28]:28s} ERR {r['err']}"); continue
        # TCR-calibrated gate: engages the peptide ~TCR-level AND docks on the groove platform
        # (helix+peptide, like real selective TCRs f_pep~0.22-0.26); NOT a high-f_pep gate (that rejects TCRs).
        on_platform = (r["f_pep"] + r["f_helix"]) >= 0.80
        flag = "OK" if (r["f_pep"] >= 0.18 and on_platform) else "  "
        good += flag == "OK"
        print(f"{r['path'][:28]:28s} {r['binder_len']:>4} {r['n_contact']:>5} {r['f_pep']:>5} {r['f_hla']:>5} {r['f_helix']:>7}  {r['pep_res']} {flag}")
    print(f"\nTCR-regime (f_pep>=0.18 & on-platform>=0.80): {good}/{len(sys.argv)-1}  [tier-2 = co-fold peptide-dependence, not f_pep]")
