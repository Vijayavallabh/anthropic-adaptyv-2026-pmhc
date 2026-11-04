#!/usr/bin/env python
"""Epitope-accessibility analysis for the KRAS G12D / HLA-A*11:01 pMHC challenge.

Quantifies, from the real crystal structures, whether peptide position 6 (the G12D-defining
residue D6, vs WT G6) is solvent/TCR-accessible on the peptide-MHC surface a NEW binder would see,
and where its carboxylate points -- i.e. whether single-residue discrimination is physically feasible
and where a complementary "gatekeeper" residue should sit.

Method: Shrake-Rupley SASA (Biopython) on (a) the pMHC-only surface (TCR stripped: chains HLA+b2m+peptide)
and (b) the full crystal complex (TCR present). The pMHC-only SASA = the surface our binder sees; the
(pMHC-only - full) difference on P6 = how much the native TCR buries P6 (does the TCR read the mutation).

Assistant-drafted (Claude) for anthropic-adaptyv-2026-pmhc, 2026-10-27.
Run with the ambertools env python:  /home/prachh/miniconda3/envs/ambertools/bin/python
"""
import argparse, json, sys
from Bio.PDB import PDBParser, NeighborSearch
from Bio.PDB.SASA import ShrakeRupley

# Tien et al. 2013 theoretical max ASA (A^2) for relative exposure
MAXASA = {"ALA":129,"ARG":274,"ASN":195,"ASP":193,"CYS":167,"GLN":225,"GLU":223,"GLY":104,
          "HIS":224,"ILE":197,"LEU":201,"LYS":236,"MET":224,"PHE":240,"PRO":159,"SER":155,
          "THR":172,"TRP":285,"TYR":263,"VAL":174}
BACKBONE = {"N","CA","C","O","OXT"}
_3to1 = {"ALA":"A","ARG":"R","ASN":"N","ASP":"D","CYS":"C","GLN":"Q","GLU":"E","GLY":"G","HIS":"H",
         "ILE":"I","LEU":"L","LYS":"K","MET":"M","PHE":"F","PRO":"P","SER":"S","THR":"T","TRP":"W",
         "TYR":"Y","VAL":"V"}

def aa(r): return _3to1.get(r, "X")

def load_model(path):
    return PDBParser(QUIET=True).get_structure("s", path)[0]

def inventory(model):
    inv = {}
    for ch in model:
        res = [r for r in ch if r.id[0] == " "]
        inv[ch.id] = {"n": len(res),
                      "seq": "".join(aa(r.resname) for r in res),
                      "resseqs": [r.id[1] for r in res]}
    return inv

def sasa_model(path, keep):
    """Fresh-parse, drop non-kept chains + all hetero/water, compute atom SASA."""
    m = load_model(path)
    for ch in list(m):
        if ch.id not in keep:
            m.detach_child(ch.id); continue
        for r in list(ch):
            if r.id[0] != " ":
                ch.detach_child(r.id)
    ShrakeRupley(n_points=960).compute(m, level="A")
    return m

def res_sasa(res):
    tot = sum(a.sasa for a in res)
    sc = sum(a.sasa for a in res if a.name not in BACKBONE)
    return tot, sc

def analyze(path, out=None):
    full = load_model(path)
    inv = inventory(full)
    # identify chains
    pep_ids = [c for c, d in inv.items() if d["n"] <= 12 and d["seq"].startswith("VVVGA")]
    if not pep_ids:
        return {"error": "no KRAS peptide chain found", "inventory": inv}
    pep_id = pep_ids[0]
    non_pep = {c: d for c, d in inv.items() if c not in pep_ids}
    hla_id = max(non_pep, key=lambda c: non_pep[c]["n"])
    b2m_cands = {c: d for c, d in non_pep.items() if c != hla_id and 90 <= d["n"] <= 112}
    b2m_id = min(b2m_cands, key=lambda c: abs(b2m_cands[c]["n"] - 99)) if b2m_cands else None
    keep = {x for x in (hla_id, b2m_id, pep_id) if x}
    tcr_ids = [c for c in inv if c not in keep]

    pep_seq = inv[pep_id]["seq"]
    result = {"pdb": path.split("/")[-1], "chains": {c: inv[c]["n"] for c in inv},
              "pep_chain": pep_id, "pep_seq": pep_seq, "hla_chain": hla_id, "b2m_chain": b2m_id,
              "tcr_chains": tcr_ids, "pep_resseqs_resolved": inv[pep_id]["resseqs"]}

    # SASA on the pMHC-only surface (what a new binder sees) and the full complex (TCR present)
    pmhc = sasa_model(path, keep)
    fullc = sasa_model(path, set(inv.keys()))
    pep_pmhc = [r for r in pmhc[pep_id] if r.id[0] == " "]
    pep_full = {r.id[1]: r for r in fullc[pep_id] if r.id[0] == " "}

    per_pos = []
    for i, r in enumerate(pep_pmhc, start=1):
        tot, sc = res_sasa(r)
        rel = round(100 * tot / MAXASA.get(r.resname, 200), 1)
        rec = {"pos": i, "res": r.resname, "aa": aa(r.resname), "resseq": r.id[1],
               "sasa_total_pmhc": round(tot, 1), "sasa_sidechain_pmhc": round(sc, 1),
               "rel_exposure_pct": rel}
        if r.id[1] in pep_full:
            _, sc_full = res_sasa(pep_full[r.id[1]])
            rec["sasa_sidechain_full_withTCR"] = round(sc_full, 1)
            rec["buried_by_tcr_sidechain"] = round(sc - sc_full, 1)  # >0 => TCR covers this side chain
        per_pos.append(rec)
    result["per_position"] = per_pos

    # P6 specifics + native-TCR contacts to the P6 side chain
    p6 = next((r for r in pep_pmhc if r.id[1] == (pep_pmhc[5].id[1])), pep_pmhc[5])  # 6th resolved residue
    result["P6"] = next((p for p in per_pos if p["pos"] == 6), None)
    if tcr_ids:
        atoms = list(fullc.get_atoms())
        ns = NeighborSearch(atoms)
        p6_full = pep_full.get(pep_pmhc[5].id[1])
        contacts = []
        if p6_full:
            for a in p6_full:
                if a.name in BACKBONE:
                    continue
                for nb in ns.search(a.coord, 4.5, level="A"):
                    pc = nb.get_parent().get_parent().id
                    if pc in tcr_ids:
                        contacts.append({"p6_atom": a.name, "tcr_chain": pc,
                                         "tcr_res": nb.get_parent().resname + str(nb.get_parent().id[1]),
                                         "tcr_atom": nb.name, "d": round(a - nb, 2)})
        result["P6_tcr_sidechain_contacts"] = sorted(contacts, key=lambda x: x["d"])
    if out:
        json.dump(result, open(out, "w"), indent=2)
    return result

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("pdbs", nargs="+")
    ap.add_argument("--outdir", default=".")
    args = ap.parse_args()
    for p in args.pdbs:
        name = p.split("/")[-1].split(".")[0]
        r = analyze(p, out=f"{args.outdir}/epitope_{name}.json")
        print(f"\n===== {name}  pep={r.get('pep_seq')}  chains={r.get('chains')} =====")
        if "error" in r:
            print("  ERROR:", r["error"]); continue
        print(f"  HLA={r['hla_chain']}  b2m={r['b2m_chain']}  TCR={r['tcr_chains']}  "
              f"resolved_pep_resseqs={r['pep_resseqs_resolved']}")
        print("  pos res  rel%  sc_SASA(pMHC)  sc_SASA(+TCR)  buried_by_TCR")
        for p in r["per_position"]:
            print(f"   {p['pos']:>2} {p['aa']}  {p['rel_exposure_pct']:>5}  "
                  f"{p['sasa_sidechain_pmhc']:>10}  {p.get('sasa_sidechain_full_withTCR','  -'):>11}  "
                  f"{p.get('buried_by_tcr_sidechain','  -'):>11}")
        if r.get("P6_tcr_sidechain_contacts"):
            print(f"  P6 side-chain contacts to native TCR (<4.5A): {len(r['P6_tcr_sidechain_contacts'])}")
            for c in r["P6_tcr_sidechain_contacts"][:6]:
                print(f"     P6.{c['p6_atom']} -- {c['tcr_chain']}/{c['tcr_res']}.{c['tcr_atom']}  {c['d']}A")
