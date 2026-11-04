#!/usr/bin/env python3
"""Campaign swap-proposal reporter (READ-ONLY; never touches the locked runs/final20_ranked.tsv or
runs/submission.csv). Compares the LOCKED 20 against the b3-scale-up union top-20, both ranked by the
IDENTICAL `sel` ruler (produced by assemble_final20.py --with-campaign --out-prefix runs/campaign/combined_).

Inputs:
  runs/final20_ranked.tsv                 - the LOCKED incumbents (old portfolio)
  runs/campaign/combined_final20_ranked.tsv - the union top-20 (proposed new portfolio, same selection logic)
  runs/campaign/combined_all_ranked.tsv   - the full sel-sorted union (incumbents + b3), for axis lookup
  runs/campaign/mpnn_diff.tsv             - orthogonal MPNN delta (enrichment annotation; JDI/Poole controls)

A swap (drop incumbent I, add b3 design D) is DOMINANT only if D's higher `sel` is not bought by regressing a
KEY selectivity axis: spec_scram (higher better), bh_e (LOWER better = tier-2 peptide-dependence, the major
discriminator), promisc_margin (higher better). Trades that raise sel but lose >=2 key axes are flagged CHURN
(lesson-portfolio-swap-verify-all-axes-same-pipeline / lesson-score-swaps-on-the-ranking-ruler). MPNN delta is
reported as an orthogonal tier-1 enrichment tiebreaker, never a gate (weak prior).
Usage: python3 scripts/campaign_select.py [--root runs/campaign]"""
import csv, os, argparse

R = "/home/prachh/v/anthropic-adaptyv-2026-pmhc"


def rd(p):
    return list(csv.DictReader(open(p), delimiter="\t")) if os.path.exists(p) else []


def f(x, d=None):
    try:
        return float(x)
    except Exception:
        return d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=f"{R}/runs/campaign")
    ap.add_argument("--mpnn", default="mpnn_diff.tsv",
                    help="MPNN delta file (relative to --root, or absolute); merged survivors+incumbents = mpnn_diff_all.tsv")
    a = ap.parse_args()
    locked = rd(f"{R}/runs/final20_ranked.tsv")
    union20 = rd(f"{a.root}/combined_final20_ranked.tsv")
    allrows = rd(f"{a.root}/combined_all_ranked.tsv")
    if not union20 or not allrows:
        print("ERROR: run  python3 scripts/assemble_final20.py --with-campaign "
              f"--out-prefix {a.root}/combined_  first (campaign score files must exist).")
        return
    axis = {r["name"]: r for r in allrows}          # name -> all axes+sel (union; same ruler)
    mprows = rd(a.mpnn if os.path.isabs(a.mpnn) else f"{a.root}/{a.mpnn}")
    mpkey = "name" if (mprows and "name" in mprows[0]) else "design"  # mpnn_differential.py writes 'design'
    mp = {r[mpkey]: r for r in mprows}
    dcol = "delta" if (mp and "delta" in next(iter(mp.values()))) else \
           ("mpnn_delta" if (mp and "mpnn_delta" in next(iter(mp.values()))) else None)

    def dlt(nm):
        return f(mp.get(nm, {}).get(dcol)) if (dcol and nm in mp) else None

    # controls reference so delta is interpretable
    for cname in ("JDI", "Poole", "7PB2", "7OW6"):
        hit = next((k for k in mp if cname.lower() in k.lower()), None)
        if hit and dcol:
            print(f"  control {cname:6s} delta={f(mp[hit][dcol]):+.3f} (argmaxD={f(mp[hit].get('argmax_frac_D')):.2f})")
    old = [r["name"] for r in locked]
    new = [r["name"] for r in union20]
    entered = [n for n in new if n not in old]
    dropped = [n for n in old if n not in new]
    is_b3 = lambda n: axis.get(n, {}).get("lineage", "").endswith("-b3")
    print(f"\n{'='*78}\nUNION TOP-20 (proposed), same sel ruler  [* = NEW b3 design]\n{'='*78}")
    print(f"{'#':>2} {'name':16s} {'lineage':20s} {'sel':>5} {'spcS':>5} {'bh_e':>5} {'grip':>5} {'pmrg':>6} {'mpnnD':>6}")
    for i, r in enumerate(union20, 1):
        nm = r["name"]; d = dlt(nm)
        ds = f"{d:+.3f}" if d is not None else "  -"
        mark = " *" if is_b3(nm) else ""
        print(f"{i:>2} {nm:16s} {r.get('lineage',''):20s} {f(r['sel']):>5.2f} {f(r['spec_scram']):>5.2f} "
              f"{f(r['bh_e']):>5.2f} {f(r.get('grip') or 0):>5.2f} {f(r.get('promisc_margin') or 0):>6.2f} {ds:>6}{mark}")

    if not entered:
        print(f"\nNO SWAPS: no b3 design cracked the union top-20. The locked 20 STANDS.")
    else:
        print(f"\n{'='*78}\nSWAP TRADES  ({len(entered)} b3 enter, {len(dropped)} incumbents drop)\n{'='*78}")
        keyhdr = f"{'axis':14s} {'spec_scram':>11} {'bh_e(lower)':>12} {'promisc_mrg':>12} {'grip':>6} {'sel':>6} {'mpnnD':>7}"
        # pair entered vs dropped by sel rank (highest-sel entrant displaces lowest-sel incumbent that fell out)
        ent_s = sorted(entered, key=lambda n: -f(axis.get(n, {}).get("sel") or -9))
        drp_s = sorted(dropped, key=lambda n: -f(axis.get(n, {}).get("sel") or -9))
        dom = churn = 0
        for k, en in enumerate(ent_s):
            dp = drp_s[k] if k < len(drp_s) else None
            e = axis.get(en, {})
            print(f"\n[swap {k+1}] ADD {en} ({e.get('lineage','')})  <->  DROP {dp or '(net-add)'}")
            print("  " + keyhdr)
            def row(tag, nm):
                r = axis.get(nm, {}); d = dlt(nm)
                print(f"  {tag:14s} {f(r.get('spec_scram') or 0):>11.3f} {f(r.get('bh_e') or 0):>12.3f} "
                      f"{f(r.get('promisc_margin') or 0):>12.3f} {f(r.get('grip') or 0):>6.3f} "
                      f"{f(r.get('sel') or 0):>6.3f} {(f'{d:+.3f}' if d is not None else '-'):>7}")
            row("ADD(b3)", en)
            if dp:
                row("DROP(locked)", dp)
                ed, dd = axis.get(en, {}), axis.get(dp, {})
                worse = 0
                worse += f(ed.get("spec_scram") or 0) < f(dd.get("spec_scram") or 0) - 0.02
                worse += f(ed.get("bh_e") or 0) > f(dd.get("bh_e") or 0) + 0.02      # bh_e lower=better
                worse += f(ed.get("promisc_margin") or 0) < f(dd.get("promisc_margin") or 0) - 0.02
                if worse >= 2:
                    churn += 1; print(f"  -> CHURN RISK: higher sel but regresses {worse}/3 key selectivity axes; HOLD incumbent.")
                else:
                    dom += 1; print(f"  -> DOMINANT: improves sel without regressing >=2 key axes. RECOMMEND swap.")
            else:
                dom += 1; print(f"  -> net add (no incumbent displaced at this rank).")
        print(f"\nVERDICT: {dom} dominant swap(s) recommended, {churn} churn-risk (hold). "
              f"Locked 20 untouched; this is a PROPOSAL (upload user-gated).")


if __name__ == "__main__":
    main()
