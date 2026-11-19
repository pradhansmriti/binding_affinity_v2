# Reproduction checklist

Working standard: compare with the paper for ballpark agreement and scientific plausibility. Keep unresolved provenance questions in [the author email draft](AUTHOR-EMAIL-DRAFT.md); do not send without an explicit request.

- [ ] **1. Assess predictions.** Residual and error analysis is assigned to the research workstream. Its completion has not been verified in this worktree.
- [ ] **2. Audit train–evaluation similarity.** Assigned to the research workstream; its completion has not been verified here.
- [x] **3. Evaluate Mpro and EGFR with the frozen RF-Score models.** Both released cohorts were evaluated, results and exact-ID overlap audited, and compared with the paper. See [target results](TARGET-RESULTS.md). The three-seed results and the exploratory BDB2020+-best seed comparison are recorded; target similarity and the authors' exact label, unit and selection conventions remain open.
- [ ] **4. Reproduce the remaining model and docked-pose evaluations.** In progress: [DeepDTA](deepdta-results.md) has been evaluated with one released checkpoint, with substantial BDB2020+ sensitivity to sequence handling; independent retraining and target evaluations remain open. [IGN](ign-REPRODUCTION.md) passed a checkpoint smoke test but requires validated pocket and graph preprocessing for benchmark evaluation. [Vina](VINA-INVESTIGATION.md) remains blocked on matching software and receptor preparation. The docked-pose experiments remain open. Results, cohorts and preprocessing are not yet equivalent across models.
- [ ] **5. Compare training-label policies.** Hold evaluation cohorts and model settings fixed and report sample sizes as well as performance. This is an independent research extension.
