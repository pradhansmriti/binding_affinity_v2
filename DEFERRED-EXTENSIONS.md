# Complete research backlog

The fixed internal and BDB2020+ RF-Score baselines have been evaluated locally. Independent experiments may proceed alongside the remaining paper-reproduction evaluations. E01–E09 have not been started; effort and priority below retain the user's original ratings.

## Current baseline

| ID | Research question | Proposed experiment | Effort | Priority | Status |
|---|---|---|---|---|---|
| E00 | Can we reproduce the LP-PDBBind paper's reported results? | Reconcile benchmark settings with the peer-reviewed journal article and supplement; audit official data; repair and run the RF-Score baseline; compare version-matched metrics, then evaluate the frozen model on the independent benchmark. | To assess | First | Internal and BDB2020+ baselines evaluated locally; author settings and additional paper evaluations remain open |

See [reproduction plan and checklist](README.md) for prerequisites, source issues, and the first-run protocol.

## Independent research backlog

| ID | Research question | Proposed experiment | Effort | Priority | Status |
|---|---|---|---|---|---|
| E01 | Does affinity label quality affect generalization? | Compare training on all labels vs. exact K_d/K_i, using the same clean test set. | Low | High | Deferred |
| E02 | How much does similarity leakage inflate performance? | Compare random, protein-disjoint, scaffold-disjoint, and joint-disjoint splits. | Medium | High | Deferred |
| E03 | How sensitive is performance to similarity thresholds? | Sweep protein sequence similarity thresholds (0.3, 0.5, 0.7). | Medium | High | Deferred |
| E04 | Do Morgan fingerprints adequately measure chemical novelty? | Compare fingerprint radii, Dice vs. Tanimoto similarity, and scaffold overlap. | Low | Medium | Deferred |
| E05 | Can proteins with low sequence similarity have similar binding interactions? | Identify protein pairs with low global sequence identity but high interaction-fingerprint similarity. | High | Medium | Deferred |
| E06 | Does QED filtering introduce chemical selection bias? | Analyze errors across QED, ligand size, and unusual chemical groups. | Low | Medium | Deferred |
| E07 | Does similarity to training data predict model error? | Plot prediction error against nearest-neighbor similarity. | Medium | High | Deferred |
| E08 | Do interaction fingerprints adequately represent structural similarity? | Compare interaction fingerprints with 3D binding-pocket structural alignment. | High | Medium | Deferred |
| E09 | Does training neighborhood density affect prediction accuracy? | Analyze error against the number of similar training examples. | Medium | Medium | Deferred |

### Later candidate: sequence search and splitting

Compare the paper's global Needleman–Wunsch protein similarity with MMseqs2 sequence search as a complementary similarity audit and possible basis for alternative splits. Record sequence identity, alignment coverage, search sensitivity, and unmatched sequences; compare nearest training neighbors, split membership, retained sample counts, and model performance. Check method differences before interpreting disagreements as violations of the paper's threshold. This candidate is for later stages and has not been started; it can inform E02, E03, and E07.

The baseline comparisons have been reviewed with limitations recorded; unresolved author details do not block independent audits. The user has chosen to begin independent research alongside remaining paper evaluations. The peer-reviewed journal supplement specifies ligand QED > 0.2 as a CL1 criterion; before E06, audit how the released flags and selected rows implement it.

Provenance: E01–E09 restored from the user's complete research backlog supplied in this chat. Formatting has been normalized; scientific scope and effort/priority ratings are preserved.

## Plan of action

1. **Data and split audit:** independently recalculate the paper's protein sequence and ligand similarity measures on the selected train, validation, and test cohorts, then examine protein–ligand interaction similarity. Report nearest training neighbors, coverage, missing inputs, and any apparent threshold violations; check method and input differences before drawing conclusions. Assess BDB2020+ separately. Identical PDB IDs alone do not establish similarity or its absence.
2. **Error analysis (E07):** relate the frozen baseline's per-complex errors to nearest-training similarity. Treat findings as exploratory, especially because internal test and BDB2020+ results have already been inspected.
3. **Evaluation design (E02–E03):** compare random, protein-disjoint, scaffold-disjoint, and jointly controlled splits, and study protein-similarity thresholds. Report split membership, retained samples, and coverage alongside performance; control differences in cohorts when interpreting comparisons.
4. **Training-data policy (E01):** compare all eligible training labels against exact Kd/Ki labels while holding the clean evaluation cohort fixed; report label composition and training coverage.
5. **Feature and model design:** compare the frozen RF-Score baseline with distance-binned atom-pair counts and chemistry-aware interaction descriptors. First hold split, label policy, forest configuration, and seeds fixed; derive any feature selection from training only. Consider ligand and pocket properties and 3D representations later, distinguishing changes in representation from changes in model. The baseline has 81 possible element-pair counts, of which 36 occur in training.

Continue the paper's Mpro and EGFR ranking and docked-pose evaluations in parallel with these research stages. They do not need to gate the similarity audit. Preserve the frozen baseline and predefine comparison protocols; repeated use of already inspected evaluation data yields exploratory results, not a fresh final test. More informative features are hypotheses, not established improvements. MMseqs2 remains a later candidate as specified above.
