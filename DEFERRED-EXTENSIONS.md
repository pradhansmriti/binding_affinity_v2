# Complete research backlog

Reproducibility comes first. E00 is the current project phase; E01–E09 are preserved follow-ups and have not been started. Effort and priority below retain the user's ratings and do not override that sequencing.

## Current baseline

| ID | Research question | Proposed experiment | Effort | Priority | Status |
|---|---|---|---|---|---|
| E00 | Can we reproduce the LP-PDBBind paper's reported results? | Confirm paper version and benchmark settings; audit official data; repair and run the RF-Score baseline; compare version-matched metrics, then evaluate the frozen model on the independent benchmark. | To assess | First | Data acquisition, metadata audit, and basic structure parsing complete; training pending prerequisites |

See [reproduction plan and checklist](README.md) for prerequisites, source issues, and the first-run protocol.

## Deferred extensions

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

Release gate: review the version-matched baseline and independent benchmark, resolve material discrepancies, then prioritize extensions with the user. Before E06, establish whether and where QED filtering applies in the selected paper/data version; its inclusion here records a research question, not a verified benchmark assumption.

Provenance: E01–E09 restored from the user's complete research backlog supplied in this chat. Formatting has been normalized; scientific scope and effort/priority ratings are preserved.
