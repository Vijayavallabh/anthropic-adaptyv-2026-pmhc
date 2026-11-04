#!/usr/bin/env python3
"""Build the BoltzGen/Boltz target CIF for the ORDERED G12D pMHC (A=HLA-A*11:01, B=b2m, C=peptide
VVVGADGVGK; TCR + ligands + waters stripped) FROM the raw RCSB 7OW6.cif so _entity_poly_seq survives
(BoltzGen/Boltz need it; a PDB->CIF convert drops it -- the f02 lesson). Also emits the peptide-centric
BoltzGen spec: binding on the EXPOSED bulge C4,C5,C7,C8 (P7 apex 74 A^2, P8 Val 37, P4 35, P5 29) --
NOT the buried discriminator P6 (8.3 A^2, points inward) and NOT the conserved a1/a2 helices.
Run with gemmi-capable python (ambertools or the boltzgen venv).
"""
import gemmi, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = f"{ROOT}/data/pdb/7OW6.cif"
OUTC = f"{ROOT}/data/targets/g12d_pmhc.cif"
SPECDIR = f"{ROOT}/specs/boltzgen"
os.makedirs(SPECDIR, exist_ok=True); os.makedirs(os.path.dirname(OUTC), exist_ok=True)

st = gemmi.read_structure(RAW); st.setup_entities()
m = st[0]
for cid in [c.name for c in m]:
    if cid not in ("A", "B", "C"):
        m.remove_chain(cid)
st.remove_ligands_and_waters(); st.remove_empty_chains(); st.setup_entities()
st.make_mmcif_document().write_file(OUTC)
txt = open(OUTC).read()
assert "_entity_poly_seq" in txt and "ATOM" in txt, "CIF missing entity_poly_seq/atoms"

chains = {c.name: len([r for r in c]) for c in st[0]}
pep = [r.name for r in st[0]["C"]]
assert len(pep) == 10, f"peptide C has {len(pep)} residues: {pep}"
print("wrote", OUTC, "chains", chains)

HOT = "4,5,7,8"  # peptide-directed only. NO not_binding on helices: it evicts binders from the groove
# (known selective TCRs are 75% helix-contact -- specificity is peptide-DEPENDENCE, not peptide-fraction).
spec = f"""# pMHC peptide-centric BoltzGen spec: de-novo binder vs ORDERED G12D pMHC (VVVGADGVGK / HLA-A*11:01).
# Binding directed to the EXPOSED central bulge C4,C5,C7,C8 (NOT buried P6, NOT the conserved a1/a2 helices).
entities:
  - protein:
      id: G
      sequence: 55..120
  - file:
      path: {OUTC}
      include:
        - chain:
            id: A
        - chain:
            id: B
        - chain:
            id: C
      binding_types:
        - chain:
            id: C
            binding: {HOT}
      structure_groups: "all"
"""
open(f"{SPECDIR}/pep_centric.yaml", "w").write(spec)
print("wrote", f"{SPECDIR}/pep_centric.yaml", "binding C:", HOT)
