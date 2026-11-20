# Binding affinity v2

V1 showed how related proteins across training and test can make affinity-prediction scores misleading. V2 reproduces LP-PDBBind's RF-Score benchmark, audits its assumptions, and tests targeted alternatives while separating established results from open hypotheses.

## Q00 — Can we reproduce the LP-PDBBind paper’s reported results?

## Q01 — Does affinity label quality affect generalization?

## Q02 — How much does similarity leakage inflate performance?

## Q03 — How sensitive is performance to similarity thresholds?

## Q04 — Do Morgan fingerprints adequately measure chemical novelty?

## Q05 — Can proteins with low sequence similarity have similar binding interactions?

## Q06 — Does QED filtering introduce chemical selection bias?

## Q07 — Does similarity to training data predict model error?

## Q08 — Do interaction fingerprints adequately represent structural similarity?

## Q09 — Does training neighborhood density affect prediction accuracy?

## Research notebook

[TODO and status](TODO.md) · [Experiment summaries](experiments/) · [Detailed original overview and commands](RESEARCH-OVERVIEW.md) · [Complete backlog and protocol](DEFERRED-EXTENSIONS.md)

[Baseline results and caveats](BASELINE-RESULTS.md) · [Reproduction notes](REPRODUCTION-NOTES.md) · [Paper–code reconciliation](PAPER-CODE-RECONCILIATION.md) · [Next steps](NEXT-STEPS.md)

The original detailed logs remain the evidence. E00 is ongoing; E01–E09 are deferred, with no results reported. The [journal article](https://doi.org/10.1021/acs.jpcb.5c08598) and [pinned upstream source](https://github.com/THGLab/LP-PDBBind/tree/cc363f80a6a696d562f290a87aa20173e60f6c52) are the reproduction references.
