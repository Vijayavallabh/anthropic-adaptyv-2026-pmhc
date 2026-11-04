#!/usr/bin/env python3
"""Triage BoltzGen design cifs (the co-designed binder+pMHC pose) with CHEAP, no-GPU pre-gates:
  * binder sequence + length (submission range 10-250)
  * NOVELTY: ungapped best-offset %id to b2m / HLA / peptide -> drop near-copies (the ~7% b2m-mimics)
  * CONTACT regime (on the BoltzGen pose): f_pep, f_helix; TCR-calibrated gate f_pep>=0.18 & on-platform>=0.80
PASS = f_pep>=0.18 & (f_pep+f_helix)>=0.80 & id_b2m<0.5 & id_hla<0.5 & 10<=len<=250.
Emits <out>/triage.tsv (all) + <out>/passing.csv (name,sequence) for the 3-state co-fold.
Run: ambertools py -I.  Usage: triage_designs.py --glob '...*.cif' --arm protein --out runs/triage_protein
"""
import argparse, glob, csv, os
from collections import defaultdict
from Bio.PDB import MMCIFParser, NeighborSearch
_3 = {"ALA":"A","ARG":"R","ASN":"N","ASP":"D","CYS":"C","GLN":"Q","GLU":"E","GLY":"G","HIS":"H","ILE":"I",
      "LEU":"L","LYS":"K","MET":"M","PHE":"F","PRO":"P","SER":"S","THR":"T","TRP":"W","TYR":"Y","VAL":"V"}
B2M = "IQRTPKIQVYSRHPAENGKSNFLNCYVSGFHPSDIEVDLLKNGERIEKVEHSDLSFSKDWSFYLLYYTEFTPTEKDEYACRVNHVTLSQPKIVKWDRDM"
HLA = "GSHSMRYFYTSVSRPGRGEPRFIAVGYVDDTQFVRFDSDAASQRMEPRAPWIEQEGPEYWDQETRNVKAQSQTDRVDLGTLRGYYNQSEDGSHTIQIMYGCDVGPDGRFLRGYRQDAYDGKDYIALNEDLRSWTAADMAAQITKRKWEAAHAAEQQRAYLEGRCVEWLRRYLENGKETLQRTDPPKTHMTHHPISDHEATLRCWALGFYPAEITLTWQRDGEDQTQDTELVETRPAGDGTFQKWAAVVVPSGEEQRYTCHVQHEGLPKPLTLRWELSSQPT"
HELIX = set(range(57, 86)) | set(range(138, 181))

def seqof(res): return "".join(_3.get(r.resname, "X") for r in res)
def best_id(a, b):
    best = 0.0
    for off in range(-6, 7):
        cnt = mm = 0
        for i in range(len(a)):
            j = i + off
            if 0 <= j < len(b): cnt += 1; mm += (a[i] == b[j])
        if cnt >= 20: best = max(best, mm / cnt)
    return best

def analyze(path):
    m = MMCIFParser(QUIET=True).get_structure("s", path)[0]
    ch = {c.id: [r for r in c if r.id[0] == " "] for c in m}
    seqs = {cid: seqof(res) for cid, res in ch.items()}
    hla = b2m = pep = binder = None
    for cid, s in seqs.items():
        if s.startswith("GSHSMRY"): hla = cid
        elif s.startswith("IQRTP"): b2m = cid
        elif s.startswith("VVVGA") and len(s) <= 12: pep = cid
    for cid in ch:
        if cid not in (hla, b2m, pep): binder = cid
    if not (hla and pep and binder): return None
    bseq = seqs[binder]
    tgt = [a for cid in (hla, b2m, pep) if cid for r in ch[cid] for a in r]
    ns = NeighborSearch(tgt); con = defaultdict(int)
    for r in ch[binder]:
        for a in r:
            for nb in ns.search(a.coord, 5.0):
                pr = nb.get_parent(); con[(pr.get_parent().id, pr.id[1])] += 1
    tot = sum(con.values()) or 1
    fpep = sum(v for (c, ri), v in con.items() if c == pep) / tot
    fhel = sum(v for (c, ri), v in con.items() if c == hla and ri in HELIX) / tot
    return dict(seq=bseq, blen=len(bseq), fpep=round(fpep, 3), fhelix=round(fhel, 3),
                onplat=round(fpep + fhel, 3), id_b2m=round(best_id(bseq, B2M), 2), id_hla=round(best_id(bseq, HLA), 2))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--glob", required=True)
    ap.add_argument("--arm", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    files = sorted(glob.glob(a.glob))
    rows = []
    for i, f in enumerate(files):
        try:
            r = analyze(f)
        except Exception as e:
            r = None
        if not r: continue
        r["name"] = f"{a.arm}_{i:04d}"
        r["cif"] = f
        r["pass"] = (r["fpep"] >= 0.18 and r["onplat"] >= 0.80 and r["id_b2m"] < 0.5
                     and r["id_hla"] < 0.5 and 10 <= r["blen"] <= 250)
        rows.append(r)
    cols = ["name", "arm", "blen", "fpep", "fhelix", "onplat", "id_b2m", "id_hla", "pass", "cif", "seq"]
    with open(f"{a.out}/triage.tsv", "w", newline="") as fh:
        w = csv.writer(fh, delimiter="\t"); w.writerow(cols)
        for r in rows: w.writerow([r.get("name"), a.arm] + [r[c] for c in ["blen","fpep","fhelix","onplat","id_b2m","id_hla","pass","cif","seq"]])
    passing = [r for r in rows if r["pass"]]
    with open(f"{a.out}/passing.csv", "w", newline="") as fh:
        w = csv.writer(fh); w.writerow(["name", "sequence"])
        for r in passing: w.writerow([r["name"], r["seq"]])
    print(f"[triage {a.arm}] analyzed {len(rows)}/{len(files)} ; PASS {len(passing)} -> {a.out}/passing.csv")
    if rows:
        import statistics as st
        print(f"  f_pep median {st.median(r['fpep'] for r in rows):.2f}  b2m-mimic(id>=0.5) {sum(r['id_b2m']>=0.5 for r in rows)}  "
              f"len {min(r['blen'] for r in rows)}-{max(r['blen'] for r in rows)}")

if __name__ == "__main__":
    main()
