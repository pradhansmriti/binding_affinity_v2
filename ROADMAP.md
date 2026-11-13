# Binding affinity v2 roadmap

The project studies how binding-affinity models generalize to new protein–ligand complexes. Work is sequenced so the benchmark is reproduced before interpreting proposed extensions. The scope and order of later work can change as evidence emerges.

## Reporting principle

When reporting numerical results, especially results based on distributions, include an appropriate plot alongside summary statistics. Choose plots that show the underlying data and relevant variation or uncertainty where practical, and label cohorts, units, and sample sizes. Apply this principle to future benchmark evaluations and experiments.

## Stage 1 — Reproduce LP-PDBBind (current)

- [x] Pin the upstream source, audit metadata, and acquire the original PDBbind v2020 structures.
- [x] Verify file coverage and basic parsing for the 10,522 selected complexes.
- [ ] Reconcile the remaining RF-Score settings, affinity units, and energy conversion; the peer-reviewed journal supplement has been reviewed.
- [x] Establish and verify an isolated project environment and complete a small smoke run.
- [x] Complete the fixed RF-Score training and internal evaluation pipeline.
- [x] Generate all descriptors, validate the 36-feature training-only mask count, and run a small train/validation smoke test.
- [x] Freeze the fixed protocol and run the full internal baseline.
- [x] Plot internal-cohort measured labels and predictions for the three seeds.
- [ ] Audit BDB2020+ and evaluate the frozen models on that independent benchmark.
- [ ] Record discrepancies and limitations before drawing reproduction conclusions.

See [next steps](NEXT-STEPS.md), [reproduction notes](REPRODUCTION-NOTES.md), and [prerequisite findings](PREREQUISITES.md) for the detailed protocol and evidence. The internal baseline results are in [baseline results](BASELINE-RESULTS.md); the independent benchmark remains pending.

## Stage 2 — Audit generalization and benchmark assumptions

After reviewing Stage 1, prioritize the preserved questions about affinity labels, protein and ligand similarity, novelty measures, chemical selection, and model error. The nine proposed experiments and their original effort/priority ratings are in [the research backlog](DEFERRED-EXTENSIONS.md); all remain unstarted.

## Stage 3 — Test remedies and synthesize findings

For issues supported by Stage 2 evidence, design matched comparisons and quantify uncertainty, performance, and any coverage tradeoffs. Document the original claims, reproduced outcomes, observed discrepancies, and limits of each conclusion. Concrete experiments depend on the earlier results.
