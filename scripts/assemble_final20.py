#!/usr/bin/env python3
"""Assemble the front-loaded, diverse, HARD-FILTERED final <=20 from all gated lineages, on the corrected
selectivity-first axes (post red-team). Single source of truth for selection.

Axes per candidate (higher=better unless noted): spec_scram = ipsae(g12d)-ipsae(scram) [sequence specificity];
grip = f_pep (binder->peptide contact fraction) vs should-fail-decoy ceiling 0.28; bh_e = empty-HLA binding
(LOWER better = real tier-2); bp = ipsae(g12d) affinity (MINOR, not front-load driver); esm monomer pLDDT;
af_rmsd (proteins, LOWER better); maxtm structural novelty (LOWER better); nliab developability (LOWER better).
HARD DROP: Ig-fold (antibody V-domain mislabeled protein), low-complexity run>=5/any-AA>30%, af2ig-fail(rmsd>=2
for proteins). Platform readers (spec_scram<0.10) kept only as late reserve. Front-load by a selectivity
conjunction score; enforce lineage/class diversity in the top. Emits runs/final20_ranked.tsv + runs/submission.csv.
Run with any python3."""
import csv, os, re, json
import argparse, glob as _glob
R = "/home/prachh/v/anthropic-adaptyv-2026-pmhc"
CEIL = 0.28
_ap = argparse.ArgumentParser()
_ap.add_argument("--out-prefix", default=f"{R}/runs/",
                 help="dir+basename-prefix for outputs (default = the LOCKED runs/final20_ranked.tsv + runs/submission.csv)")
_ap.add_argument("--with-campaign", action="store_true",
                 help="also ingest the b3 scale-up campaign lineage from runs/campaign/* (PROPOSAL mode; use with a non-default --out-prefix)")
_A = _ap.parse_args()
OUTP = _A.out_prefix
def rd(p):
    return list(csv.DictReader(open(p), delimiter="\t")) if os.path.exists(p) else []
def rdc(p):
    return list(csv.DictReader(open(p))) if os.path.exists(p) else []
def f(x, d=0.0):
    try: return float(x)
    except Exception: return d
jmotif = re.compile(r'[FW]G.G[TS]')
def is_ig(s):
    # ig_ss = immunoglobulin V-set topology: Cys -(~13)- conserved Trp -(~40-60)- 2nd Cys (domain disulfide).
    # Catches de-novo Ig V-domains whose motifs differ from the natural antibody consensus (WVRQ/YYC) and so
    # evade the per-motif checks (e.g. b2_gpu7_27: ...LNC..W(YKNG)..GVYLC..). Weighted x2 = a strong indicator.
    h = (s.count('C') >= 2) + bool(re.search(r'C.{8,20}W[VYFI][RQK]Q', s)) + bool(jmotif.search(s[-15:])) \
        + bool(re.search(r'(QVQL|EVQL|DIQ|DIV|EIV|QLQ|QVQ|GVQ|QSV|QVK)', s[:6])) + bool(re.search(r'Y[YFH]C[A-Z]{3,}', s)) \
        + 2 * bool(re.search(r'C.{8,18}W.{25,65}C', s))
    return h >= 3
def maxrun(s):
    m = c = 1
    for i in range(1, len(s)):
        c = c + 1 if s[i] == s[i-1] else 1; m = max(m, c)
    return m
def lowc(s): return (not s) or maxrun(s) >= 5 or max(s.count(a)/len(s) for a in set(s)) > 0.30

def sel_score(c):
    # Rank by the 3-tier rubric. tier-1 (G12D-vs-WT) is co-fold-BLIND -> proxied by two specificity axes:
    # spec_scram (sequence ORDER, vs scramble) + promisc_margin (peptide IDENTITY, vs unrelated A*11:01
    # peptides). tier-2 (peptide-DEPENDENCE) is a TIER, measured DIRECTLY as the empty-HLA interface bh_e
    # (LOWER=better) -> a MAJOR reward 0.6*(1-bh_e), not the old token penalty. tier-3 (affinity bp) + grip
    # quality + foldability (esm) are minor. The 5-sample bh_e split (0103/0202/0081 clean <0.4; 0155/0025/
    # 0369/0073/0092 bind empty >0.65) is what this term resolves.
    # structural-novelty penalty (hard-gate hedge): nanobodies judged on CDR -> exempt. Proteins: TM<0.89 safe
    # (0), 0.89-0.92 moderate (-0.12), >=0.92 strong (-0.3) -- prefer novelty-SAFE picks now that batch-2 supplies
    # selective low-TM candidates, without hard-dropping the high-TM grippers (they likely still clear >=3 via seq).
    t = c.get("maxtm", 0.0) if c.get("tm_measured") else 0.0
    nov_pen = 0.0 if c["cls"] == "nanobody" else (0.3 if t >= 0.92 else (0.12 if t >= 0.89 else 0.0))
    s = (max(0.0, c["spec_scram"]) + 0.4*max(0.0, c.get("promisc_margin") or 0.0)       # tier-1 proxy
         + 0.6*(1.0 - min(max(c["bh_e"], 0.0), 1.0))                                     # tier-2 peptide-dependence
         + 0.5*max(0.0, c["grip"] - CEIL)                                                # peptide grip quality
         + 0.2*c["bp"] + 0.2*(c["esm"]/100.0)                                            # tier-3 affinity + foldability
         - 0.05*c["nliab"] - nov_pen                                                     # developability + novelty
         - (0.5 if c["spec_scram"] < 0.10 else 0))                                       # platform demote
    return round(s, 3)

cands = []
# promiscuity reference: binder binding to UNRELATED A*11:01 peptides (atic/ebna4) -- a design that grips
# an unrelated peptide ~as well as g12d is a pan-peptide reader (fails tiers 1+2), demote like a platform
# reader. pepswap_full_3samp has proteins+nanobodies; RFd uses its re-validation file (joined below).
pepfull = {r["name"]: r for r in rd(f"{R}/runs/pepswap_full_3samp.tsv")}
# --- de-novo proteins (boltzgen-protein) from corrected scorecard_v2 + seqs ---
seqs = {r["name"]: r["seq"] for r in rd(f"{R}/runs/final_protein.tsv")}
for r in rd(f"{R}/runs/protein_scorecard_v2.tsv"):
    nm = r["name"]; seq = seqs.get(nm, ""); pf = pepfull.get(nm, {})
    cands.append(dict(name=nm, cls="protein", lineage="boltzgen-protein", seq=seq,
                      spec_scram=f(r["spec_scram"]), grip=f(r["fpep"]), bh_e=f(r["bh_e"]), bp=f(r["bp"]),
                      esm=f(r["esm"]), af_rmsd=f(r["afr"], 9), maxtm=f(r["maxtm"]), nliab=f(r["nli"]),
                      dq=r["dq"], atic=f(pf.get("atic")), ebna4=f(pf.get("ebna4")),
                      g12d_ips=f(pf.get("g12d", r["bp"]))))
# --- nanobodies (boltzgen-vhh) ---
nbspec = {r["name"]: r for r in rd(f"{R}/runs/pepswap_full_3samp.tsv") if r["name"].startswith("nanobody")}
nbgrip = {r["name"]: r for r in rd(f"{R}/runs/nb_grip.tsv")}
nbmeta = {r["name"]: r for r in rd(f"{R}/runs/final_nanobody.tsv")}
for nm, sp in nbspec.items():
    m = nbmeta.get(nm, {}); g = nbgrip.get(nm, {})
    seq = m.get("seq", "")
    cands.append(dict(name=nm, cls="nanobody", lineage="boltzgen-vhh", seq=seq,
                      spec_scram=round(f(sp["g12d"]) - f(sp["scram"]), 3), grip=f(g.get("fpep_mean")),
                      bh_e=f(m.get("bh_e")), bp=f(m.get("bp_ipsae")), esm=f(m.get("af_plddt_b")),
                      af_rmsd=0.0, maxtm=0.0, nliab=0.0, dq="-",
                      atic=f(sp["atic"]), ebna4=f(sp["ebna4"]), g12d_ips=f(sp["g12d"])))
# --- RFd (rfd lineage): PREFER the multi-sample re-validation (rfd_val.tsv -- real bh_e, 5-sample spec
#     + promiscuity); fall back to the noisy single-sample rfd_pepswap with a NEUTRAL bh_e placeholder. ---
rfdseq = {r["name"]: r["sequence"] for r in rdc(f"{R}/runs/rfd/rfd_survivors.csv")}
rfdval = {r["name"]: r for r in rd(f"{R}/runs/rfd/rfd_val.tsv")}
rfdvgrip = {r["name"]: r for r in rd(f"{R}/runs/rfd/rfd_val_grip.tsv")}
if rfdval:
    for nm, v in rfdval.items():
        g = rfdvgrip.get(nm, {})
        cands.append(dict(name=nm, cls="protein", lineage="rfd", seq=rfdseq.get(nm, ""),
                          spec_scram=f(v["spec_scram"]), grip=f(g.get("fpep_mean")), bh_e=f(v["bh_e"]),
                          bp=f(v["g12d"]), esm=85.0, af_rmsd=1.0, maxtm=0.6, nliab=0.0, dq="-",
                          atic=f(v["atic"]), ebna4=f(v["ebna4"]), g12d_ips=f(v["g12d"])))
else:
    rfdspec = {r["name"]: r for r in rd(f"{R}/runs/rfd/rfd_pepswap.tsv")}
    rfdgrip = {r["name"]: r for r in rd(f"{R}/runs/rfd/rfd_grip.tsv")}
    for nm, sp in rfdspec.items():
        g = rfdgrip.get(nm, {})
        cands.append(dict(name=nm, cls="protein", lineage="rfd", seq=rfdseq.get(nm, ""),
                          spec_scram=round(f(sp["g12d"]) - f(sp["scram"]), 3), grip=f(g.get("fpep_mean")),
                          bh_e=0.70, bp=f(sp["g12d"]), esm=85.0, af_rmsd=1.0, maxtm=0.6, nliab=0.0, dq="-",
                          atic=f(sp["atic"]), ebna4=f(sp["ebna4"]), g12d_ips=f(sp["g12d"])))
# --- batch-2 de-novo proteins (2nd BoltzGen generation, peptide-centric): 5-sample reval + grip + ESMFold ---
#     The lever for more tier-2-clean grippers. Already Ig/low-complexity filtered + ESMFold pLDDT>=0.80 gated.
b2val = {r["name"]: r for r in rd(f"{R}/runs/batch2_reval.tsv")}
b2grip = {r["name"]: r for r in rd(f"{R}/runs/batch2_reval_grip.tsv")}
b2seq = {r["name"]: r["sequence"] for r in rdc(f"{R}/runs/gen_batch2_clean.csv")}
for nm, v in b2val.items():
    g = b2grip.get(nm, {})
    cands.append(dict(name=nm, cls="protein", lineage="boltzgen-protein-b2", seq=b2seq.get(nm, ""),
                      spec_scram=f(v["spec_scram"]), grip=f(g.get("fpep_mean")), bh_e=f(v["bh_e"]),
                      bp=f(v["g12d"]), esm=85.0, af_rmsd=0.0, maxtm=0.5, nliab=0.0, dq="-",
                      atic=f(v["atic"]), ebna4=f(v["ebna4"]), g12d_ips=f(v["g12d"])))
# --- batch-3 SCALE-UP campaign (BoltzGen protein + nanobody, peptide-centric, 5-sample 6-state panel) ---
#     The exhaustive-GPU generation (3000 protein + 3000 nanobody). Scored on the IDENTICAL axes as batch-2 so
#     it ranks on the same `sel` ruler. Proteins -> boltzgen-protein-b3; nanobodies (name prefix nb3_) ->
#     boltzgen-vhh-b3. OFF by default (keeps the locked run byte-reproducible); --with-campaign turns it on.
if _A.with_campaign:
    c3val = {r["name"]: r for r in rd(f"{R}/runs/campaign/panel_reval.tsv")}
    c3grip = {r["name"]: r for r in rd(f"{R}/runs/campaign/panel_grip.tsv")}
    c3seq = {r["name"]: r.get("sequence", "") for r in rdc(f"{R}/runs/campaign/panel_pool.csv")}
    for nm, v in c3val.items():
        g = c3grip.get(nm, {}); is_nb = nm.startswith("nb3")
        cands.append(dict(name=nm, cls="nanobody" if is_nb else "protein",
                          lineage="boltzgen-vhh-b3" if is_nb else "boltzgen-protein-b3", seq=c3seq.get(nm, ""),
                          spec_scram=f(v["spec_scram"]), grip=f(g.get("fpep_mean")), bh_e=f(v["bh_e"]),
                          bp=f(v["g12d"]), esm=85.0, af_rmsd=0.0, maxtm=0.0, nliab=0.0, dq="-",
                          atic=f(v["atic"]), ebna4=f(v["ebna4"]), g12d_ips=f(v["g12d"])))
# --- fab (boltzgen-fab) : filled when runs/fab_final.tsv exists ---
for r in rd(f"{R}/runs/fab_final.tsv"):
    cands.append(dict(name=r["name"], cls=r.get("cls", "fab_kappa"), lineage="boltzgen-fab", seq=r["seq"],
                      spec_scram=f(r["spec_scram"]), grip=f(r["grip"]), bh_e=f(r["bh_e"]), bp=f(r["bp"]),
                      esm=f(r.get("esm", 85)), af_rmsd=0.0, maxtm=0.4, nliab=f(r.get("nliab", 0)), dq="-"))

# 5-sample re-validation OVERRIDE (proteins+nanobodies): supersede the 3-sample scorecard for the genuine
# front-load picks. The single->5-sample RFd flip (rfd_des_246 spec 0.51->0.03) proved low-sample survivors
# must be confirmed; the front-load is the whole game, so lock it on 5-sample numbers. RFd already 5-sample.
reval = {r["name"]: r for r in rd(f"{R}/runs/reval_genuine.tsv")}
revalg = {r["name"]: r for r in rd(f"{R}/runs/reval_genuine_grip.tsv")}
for c in cands:
    c["reval"] = (c["lineage"] == "rfd")
    rv = reval.get(c["name"])
    if rv:
        c["spec_scram"] = f(rv["spec_scram"]); c["bh_e"] = f(rv["bh_e"]); c["bp"] = f(rv["g12d"])
        c["g12d_ips"] = f(rv["g12d"]); c["atic"] = f(rv["atic"]); c["ebna4"] = f(rv["ebna4"]); c["reval"] = True
        g = revalg.get(c["name"])
        if g: c["grip"] = f(g.get("fpep_mean"))

# CONSISTENT ESMFold monomer pLDDT (the foldability axis + de-novo success predictor). Overrides the mixed
# esm sources (batch-1 scorecard used ESMFold-pLDDT for proteins but af_plddt_b for nanobodies -- a DIFFERENT
# in-complex metric that read the nanobodies falsely low 38-47; monomer pLDDT shows them at 0.91/0.86).
plddt = {}
_plpaths = [f"{R}/runs/final_esm/plddt.json", f"{R}/runs/batch2_esm/plddt.json", f"{R}/runs/rfd/esm/plddt.json"]
_plpaths += sorted(_glob.glob(f"{R}/runs/campaign/esm/out*/plddt.json"))
for p in _plpaths:
    if os.path.exists(p):
        try: plddt.update(json.load(open(p)))
        except Exception: pass
for c in cands:
    if c["name"] in plddt: c["esm"] = round(plddt[c["name"]] * 100, 1); c["esm_consistent"] = True
    else: c["esm_consistent"] = False

# STRUCTURAL NOVELTY: single-seq ESMFold -> foldseek max-TM vs PDB (the novelty hard-gate's hardest axis for
# de-novo helical proteins). Calibrated 3-vs-2 boundary ~0.89 (portal-verified on TfR1); >=0.90 = novelty RISK
# (may not clear the >=3 hard gate). NANOBODIES are judged on CDR diversity (framework TM expected high) -> exempt.
tm = {}
for p in (f"{R}/runs/novelty/final_struct.csv", f"{R}/runs/novelty/batch2_struct.csv", f"{R}/runs/campaign/novelty/b3_struct.csv"):
    for r in rdc(p):
        try: tm[r["name"]] = float(r["singleseq_maxTM_pdb"])
        except Exception: pass
for c in cands:
    if c["name"] in tm: c["maxtm"] = round(tm[c["name"]], 3); c["tm_measured"] = True
    else: c["tm_measured"] = False
    c["novelty_risk"] = bool(c["cls"] != "nanobody" and c.get("tm_measured") and c["maxtm"] >= 0.90)

# hard filters
for c in cands:
    reasons = []
    if c["seq"] and c["lineage"] in ("boltzgen-protein", "boltzgen-protein-b2", "boltzgen-protein-b3", "rfd") and is_ig(c["seq"]): reasons.append("IG-FOLD")
    if c["seq"] and lowc(c["seq"].replace(":", "")): reasons.append("low-complexity")
    if c["lineage"] in ("boltzgen-protein",) and c["af_rmsd"] >= 2.0: reasons.append("af2ig-fail")
    if c["dq"] not in ("-", ""): reasons.append(c["dq"])
    c["drop"] = ",".join(sorted(set(reasons))) or ""
    # promiscuity (computed BEFORE sel, which rewards promisc_margin): g12d vs the best UNRELATED-peptide
    # bind. pan-peptide reader if margin<0.10 OR it forms a real interface to an unrelated A*11:01 peptide
    # (abs atic/ebna4 > 0.45; clean candidates are all <0.30). Either way -> reserve tail.
    g = c.get("g12d_ips"); od = [x for x in (c.get("atic"), c.get("ebna4")) if x is not None]
    c["promisc_margin"] = round(g - max(od), 3) if (g is not None and od) else None
    c["promisc"] = bool((c["promisc_margin"] is not None and c["promisc_margin"] < 0.10)
                        or (od and max(od) > 0.45))
    c["platform"] = c["spec_scram"] < 0.10
    # poor monomer foldability (consistent ESMFold pLDDT<0.72) -> unlikely to express/fold -> demote from
    # front-load (foldability is a validated de-novo success predictor). Only when we have the real metric.
    c["weakfold"] = bool(c.get("esm_consistent") and c["esm"] < 72.0)
    c["sel"] = sel_score(c)

keep = [c for c in cands if not c["drop"]]
keep.sort(key=lambda c: -c["sel"])
# NEVER front-load a platform reader (spec_scram<0.10), a promiscuous pan-peptide reader, or a poor folder
# above a genuine selective+foldable candidate -- all go to the late reserve tail.
non_plat = [c for c in keep if not c["platform"] and not c["promisc"] and not c["weakfold"]]
plat = [c for c in keep if c["platform"] or c["promisc"] or c["weakfold"]]

# pass 1: genuine candidates, sel-sorted, gentle per-lineage cap (6) to avoid a monoculture top
final = []; per = {}
for c in non_plat:
    if len(final) >= 20: break
    if per.get(c["lineage"], 0) >= 6: continue
    final.append(c); per[c["lineage"]] = per.get(c["lineage"], 0) + 1
# pass 2: any remaining genuine candidates over the cap
for c in non_plat:
    if len(final) >= 20: break
    if c not in final: final.append(c); per[c["lineage"]] = per.get(c["lineage"], 0) + 1
# pass 3: fill the tail with platform reserves (they likely won't be bench-tested; better than empty)
for c in plat:
    if len(final) >= 20: break
    final.append(c); per[c["lineage"]] = per.get(c["lineage"], 0) + 1
n_genuine = len(non_plat[:20])

cols = ["rank", "name", "cls", "lineage", "sel", "spec_scram", "grip", "bh_e", "bp", "esm", "af_rmsd", "maxtm", "nliab", "promisc_margin", "reval", "platform", "promisc", "weakfold", "novelty_risk"]
with open(f"{OUTP}final20_ranked.tsv", "w") as fo:
    fo.write("\t".join(cols) + "\n")
    for i, c in enumerate(final, 1):
        fo.write("\t".join(str(c.get(k, "") if k != "rank" else i) for k in cols) + "\n")
# full sel-sorted dump (campaign/proposal mode only) so near-misses + high-sel-but-dropped are visible
if _A.with_campaign:
    acols = ["name", "cls", "lineage", "sel", "spec_scram", "grip", "bh_e", "bp", "esm", "maxtm",
             "promisc_margin", "platform", "promisc", "weakfold", "novelty_risk", "drop"]
    with open(f"{OUTP}all_ranked.tsv", "w") as fo:
        fo.write("\t".join(acols) + "\n")
        for c in sorted(cands, key=lambda c: -c["sel"]):
            fo.write("\t".join(str(c.get(k, "")) for k in acols) + "\n")
    print(f"[campaign] full sel-sorted dump ({len(cands)} cands) -> {OUTP}all_ranked.tsv")
# --- submission.csv (name, sequence, molecule_class); fab -> "VH:VL", class kappa/lambda by VL J-motif ---
def mol_class(c):
    # Allowed classes (owner-confirmed 2026-11-01): single_chain, nanobody, scfv, fab_kappa, fab_lambda.
    # A de-novo single-chain protein binder = "single_chain" (NOT "protein").
    if c["cls"] == "protein": return "single_chain"
    if c["cls"] == "nanobody": return "nanobody"
    if c["cls"] == "scfv": return "scfv"
    vl = c["seq"].split(":")[-1]
    return "fab_lambda" if re.search(r'[FW]G.GT[KQ]L', vl[-12:]) else "fab_kappa"
with open(f"{OUTP}submission.csv", "w", newline="") as fo:
    w = csv.writer(fo); w.writerow(["name", "sequence", "molecule_class"])
    for c in final:
        w.writerow([c["name"], c["seq"], mol_class(c)])
# byte-verify format against target.yaml required_columns
req = re.search(r'required_columns:\s*\[([^\]]+)\]', open(f"{R}/configs/target.yaml").read())
reqcols = [x.strip() for x in req.group(1).split(",")] if req else []
hdr = open(f"{OUTP}submission.csv").readline().strip().split(",")
print(f"submission.csv header={hdr} required={reqcols} MATCH={hdr==reqcols}")
print(f"candidates={len(cands)} kept={len(keep)} dropped={len(cands)-len(keep)}  final={len(final)}")
print(f"GENUINE (non-platform) candidates available: {len(non_plat)}  | platform reserves: {len(plat)}")
print(f"lineage spread in final: {per}")
def _pm(c): return f"{c['promisc_margin']:>5}" if c.get("promisc_margin") is not None else "    ."
print(f"\n{'#':>2} {'name':16s} {'cls':9s} {'lineage':18s} {'sel':>5} {'spcS':>5} {'grip':>4} {'bh_e':>4} {'bp':>4} {'esm':>4} {'maxtm':>5} {'pmrg':>5} {'flag':>4} {'nov':>3}")
for i, c in enumerate(final, 1):
    flag = "PLT" if c["platform"] else ("PRO" if c["promisc"] else ("WFD" if c.get("weakfold") else "."))
    rv = "5s" if c.get("reval") else "3s"
    nov = "N!" if c.get("novelty_risk") else ("ok" if c.get("tm_measured") else "-")
    print(f"{i:>2} {c['name']:16s} {c['cls']:9s} {c['lineage']:18s} {c['sel']:>5} {c['spec_scram']:>5} {c['grip']:>4} {c['bh_e']:>4} {c['bp']:>4} {c['esm']:>4.0f} {c['maxtm']:>5} {_pm(c):>5} {flag:>4} {nov:>3}")
print("\nDROPPED:")
for c in cands:
    if c["drop"]: print(f"  {c['name']} ({c['lineage']}): {c['drop']}")
