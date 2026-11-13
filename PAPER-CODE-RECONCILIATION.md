# Paper–code reconciliation: RF-Score

Comparison target: the peer-reviewed [2026 journal article](https://doi.org/10.1021/acs.jpcb.5c08598), J. Phys. Chem. B 130, 730–740. Tables 1 and 2 were checked against the accessible [PMC author manuscript](https://pmc.ncbi.nlm.nih.gov/articles/PMC13430955/); the publisher supporting information was independently inspected on 2026-11-10 (file `jp5c08598_si_001.pdf`, SHA-256 `2c565ab2aa60e94bc750852e60557413c525855dd11269cc9b8248a7e667f1ad`). Its cleaning and RF-Score descriptions agree in the relevant points with the earlier arXiv v3 review. The author notebook and metadata are pinned to [upstream commit cc363f80a6a696d562f290a87aa20173e60f6c52](https://github.com/THGLab/LP-PDBBind/tree/cc363f80a6a696d562f290a87aa20173e60f6c52). Notebook cell numbers below are zero-based.

## Evidence and decisions

| Topic | Paper / supplement | Released notebook / metadata | Reproduction decision and remaining uncertainty |
|---|---|---|---|
| Cohort | Section 2.1 specifies CL1 train and CL2 test, with covalent binders treated separately. | Cells 9–10 filter noncovalent CL1 train and noncovalent CL2 validation/test. Current released CSV yields 7,393/958/2,171. | Adopt those exact released filters and IDs for the first run. These counts are derived from the CSV, not confirmed author RF-specific counts from a historical run. |
| Descriptors | S1.6 specifies RF-Score v1, nine elements, contacts within 12 Å, and 36 nonzero training features. | Cells 5–7 construct 9×9 protein-major pair counts with strict distance <12 Å. Cell 14 computes a training-only mask and has cached output 36, although its execution count and the surrounding cells are inconsistent. | Adopt the source's element order C/O/N/F/P/S/Cl/Br/I and strict cutoff. The full current training cohort yields 36 features, matching the paper and cached output. The notebook does not save the computed historical indices; an inactive 27-index comment differs and cannot establish the historical mask. |
| Atom parsing | The paper does not fully specify line-level parsing or prepared-coordinate provenance. | Cells 6–7 parse protein ATOM records using an atom-name lookup, and ligand SDF atoms. The notebook's ligand reader includes a special fallback for >250 atoms; its source is not a general element parser. | Preserve source behavior as far as feasible; independently document any differences. The current readers and pinned notebook readers produced identical supported atom types and coordinates for all 10,522 proteins and 10,522 ligands; see `outputs/parser-comparison.json` and `scripts/compare_notebook_parsers.py`. This checks the downloaded inputs, not author-prepared coordinate identity or chemical correctness. The current training mask retains 36 features; direct executable-notebook comparisons match all 81 counts for ten train complexes. |
| Labels and units | Table 1 identifies errors as kcal/mol. | Cells 9–10 fit CSV `value` directly. All 5,316 entries shared with the released v2020 refined index exactly match its -log affinity values. No kcal conversion appears in these RF cells. | Fit in native p-affinity units and separately report explicitly labeled energy-converted RMSE with assumptions. This mismatch does not establish which convention generated the published table. Determine the authors' conversion and temperature before a numerical equivalence claim. |
| Label policy | CL1 train is less restrictive; CL2 evaluation excludes IC50 according to Section 2.1. | Selected train rows have 2,921 IC50, 2,454 Kd, and 2,018 Ki prefixes; 172 include `<` or `>`. Validation (560 Kd, 398 Ki) and test (1,001 Kd, 1,170 Ki) have no `<` or `>` characters. Counts use the literal metadata strings, not a full assay audit. | Preserve original filters and labels, including their limitations. An IC50 value is not generally interchangeable with Kd, and an inequality is not an exact value. Separate label-policy experiments are deferred. |
| Hyperparameter selection | S1.6 does not report tree count or max_features. | Cell 16 tries 100–500 trees in steps of 50 and max_features 2–10, with seed 24. Although named `rmse_OOB`, it compares predictions on validation; the loop records the best `mtry` but not the tree count in a variable and is unexecuted in the saved notebook. Cell 17 instead fits fixed 100 trees and max_features 3. | Run the fixed 100/3 setting as a clearly labeled source-code baseline. A separately labeled validation-selected grid is an alternative, not established as the published configuration. Freeze the selection rule and settings before test evaluation. |
| Repetitions / selection | Table 1 reports mean ± SD from three initializations. | Cell 17 loops over ten models with no explicit estimator random seeds and chooses the saved model by test Pearson correlation. The saved notebook has no executed output for that training cell, and cell 17 does not calculate validation metrics. | Use three explicit project seeds (0, 1, 2); report every seed and aggregate. Do not select using the test set. These seeds and the no-test-selection rule are project choices, not recovered author settings. Do not assume a particular SD convention without stating it. |
| Reproducibility / external test | The paper presents BDB2020+ as an independent benchmark. | Cell 22 refers to obsolete BindingDB paths and attempts to reshape a descriptor dictionary. The released source is not an executable end-to-end external evaluation without repair. | The 115-row BDB2020+ release was evaluated using all frozen models and the training-derived mask without refitting or seed selection; see [baseline results](BASELINE-RESULTS.md). Similarity and assay provenance remain to be audited. Author choice of model for external evaluation remains uncertain. |

## Agreed starting settings

Use the pinned authors’ final notebook loop settings (`n_estimators=100`,
`max_features=3`) for the first baseline. These are adopted from their released
code as starting choices; we have not independently established that they are
optimal, or confirmed that they generated the paper's reported numbers.
`max_features=3` means three candidate features are sampled at each split,
not that only three features are available to the entire forest. The full-cohort training mask now retains 36 features, matching the paper’s reported count.

The notebook separately defines a two-dimensional validation search over tree
counts (100–500 in steps of 50) and candidate-feature counts (2–10). Its saved
search cell has no execution output and its final fitting loop hardcodes 100/3,
so do not describe the fixed choices as the confirmed winner of that search.
A future validation-only search would be a separate, labeled experiment.
The three explicit seeds planned for our run are our reproducibility choice,
not settings recovered from the authors.

## Why CL1 and CL2 differ

The journal supporting information, page S2, says CL1 was used for training to retain the largest
available dataset. CL2 adds the requirement that labels originate from exact
`Kd=` or `Ki=` records; the authors use it for validation and test because they
consider those labels more reliable. Thus the released training cohort includes
IC50 and non-exact records; the validation/test cohorts do not include IC50 or
inequality labels. A complex has one selected label in the released CSV; the
CSV does not by itself establish which alternative measurements were or were not
available in the literature. Preserve this distinction when interpreting the
training policy and its coverage–label-quality tradeoff.

### Which measurement becomes the label?

The PDBbind curators described a historical preference order of **Kd > Ki > IC50** when multiple measurement types were available for a complex ([Wang et al., 2015](https://academic.oup.com/bioinformatics/article/31/3/405/2365195)). We have not verified how consistently that rule was applied to the released v2020 cohort or whether the selected measurement is appropriate for each complex.

## Affinity-to-energy comparison policy

For comparison with Table 1's stated kcal/mol RMSE, keep the original released
p-affinity values as the native labels and calculate a separately labeled
energy-scale result. For exact Kd values, `Kd (M) = 10**(-pKd)` and
`ΔG° = R*T*ln(Kd / 1 M) = -R*T*ln(10)*pKd`. As an explicit project convention,
use T = 298.15 K and R = 0.00198720425864083 kcal mol⁻¹ K⁻¹, giving a factor of
approximately -1.36425 kcal/mol per p unit. For RMSE, multiply native p-unit RMSE
by the magnitude of that factor; calculate predictions and reference labels on
the same scale. This step needs no intermediate Kd calculation in code.

The authors' actual temperature and conversion convention are not established,
so the converted number is an approximate, explicitly labeled comparison, not
an exact reproduction of their reported unit treatment. Apply the same linear
scaling to the released mixed-assay labels only as an **energy-equivalent
comparison scale**: IC50 and inequality-derived values are not necessarily
thermodynamic Kd or exact binding free energies. Do not relabel all rows as Kd
or claim physical free-energy accuracy from this conversion. Preserve original
assay types and report native p-unit metrics alongside converted metrics.

## Comparison target and limits

The journal article's Table 1, as reproduced in the PMC author manuscript, reports RF-Score train 0.68 ± 0.003, validation 2.14 ± 0.01 and test 2.10 ± 0.003 kcal/mol; its Table 2 reports BDB2020+ 1.61 ± 0.008 kcal/mol and Pearson 0.51 ± 0.008. These are comparison values, not pass/fail thresholds. Do not compare native p-affinity RMSE directly against them. The fixed internal baseline has since been evaluated; see [baseline results](BASELINE-RESULTS.md).

The observed source differences do not prove that the authors used the saved notebook unchanged to generate the paper's results. Historical dataset membership, exact prepared coordinates, author software versions, tree settings, seeds, temperature, and conversion remain unresolved. The current environment snapshot is a project environment, not a recovered author environment. Preserve these distinctions in any report.

## Journal supporting information review (2026-11-10)

Pages S1–S2 describe CL1 as requiring ligand QED > 0.2, element-frequency filtering, and a protein–ligand minimum heavy-atom distance between 1.75 and 4 Å; CL2 adds exact Kd or Ki records. Page S5–S6 describes nine elements, 12 Å contacts, and 36 features with nonzero occurrence in training. It does not state the strict boundary convention, forest tree count, max_features, estimator seeds, or software version. The pinned notebook remains the source for the strict cutoff and initial 100/3 configuration.

Page S2 prints ΔG = −RT ln(K) while referring to Kd or Ki, without defining K or stating temperature. If K means a molar dissociation constant in the usual dimensionless standard-state form, the conventional expression uses +RT ln(Kd / 1 M); a minus sign would instead fit an association constant. Do not silently assume the printed symbol or sign resolves the authors’ actual conversion. The notebook unit discrepancy and the project’s explicitly labeled 298.15 K comparison convention remain open.

The journal supplement supports the QED-filtering premise of E06; whether each released flag and selected row implements that criterion still requires a data/code audit.
