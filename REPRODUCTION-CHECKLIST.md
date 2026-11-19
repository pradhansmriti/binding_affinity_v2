# Reproduction checklist

Working standard: compare with the paper for ballpark agreement and scientific plausibility. Keep unresolved provenance questions in [the author email draft](AUTHOR-EMAIL-DRAFT.md); do not send without an explicit request.

- [ ] **1. Assess predictions.** Residual and error analysis is assigned to the research workstream. Its completion has not been verified in this worktree.
- [ ] **2. Audit train–evaluation similarity.** Assigned to the research workstream; its completion has not been verified here.
- [x] **3. Evaluate Mpro and EGFR with the frozen RF-Score models.** Both released cohorts were evaluated, results and exact-ID overlap audited, and compared with the paper. See [target results](TARGET-RESULTS.md). The three-seed results and the exploratory BDB2020+-best seed comparison are recorded; target similarity and the authors' exact label, unit and selection conventions remain open.
- [ ] **4. Reproduce the remaining model and docked-pose evaluations.** Resume here next time. Inventory the paper protocols and released inputs, select the next tractable comparison, freeze the protocol, run it and document evidence and limitations. A preliminary look found the released DeepDTA checkpoint and code, while the BDB2020+ archive did not visibly contain docked poses; availability and feasibility require further verification. A preliminary input scan found nine of 2,171 internal test sequences exceed the DeepDTA notebook's nominal 2,000-residue padding length; the intended handling remains unresolved. No DeepDTA evaluation has been completed.
- [ ] **5. Compare training-label policies.** Hold evaluation cohorts and model settings fixed and report sample sizes as well as performance. This is an independent research extension.
