# Draft: RF-Score reproduction questions

**To:** Professor Teresa Head-Gordon and coauthors

**Subject:** Questions about reproducing LP-PDBBind RF-Score evaluations

Dear Professor Head-Gordon and colleagues,

I am reproducing the RF-Score experiments in your LP-PDBBind paper. Thank you for making the benchmark and code available. Using the released data and a fixed 100-tree, three-feature RF-Score configuration, we obtained results in the same general range as the paper: our three-seed internal test and BDB2020+ energy-equivalent RMSEs were approximately 2.12 and 1.65 kcal/mol, compared with 2.10 and 1.61 reported. Our Mpro result differs more: approximately 1.25 versus 1.64 kcal/mol. We would appreciate clarification of a few details if they are readily available:

1. Were the models in Tables 1–3 trained with 100 trees and `max_features=3`? Could you share the executed training and evaluation scripts, software versions, and seeds or saved models used for the reported runs?
2. The released RF notebook fits the CSV's p-affinity values, while the tables give kcal/mol. What conversion and temperature were used to calculate the reported RMSEs?
3. Table 3 uses the best model on BDB2020+. Which metric determined the best initialization, and were all reported target results produced by that one model?
4. The released Mpro metadata include `pKa_reliable` and `pKa_full`. Which labels and sample IDs were used in Table 3? Are the EGFR `value` column and all 23 released IDs the corresponding inputs?
5. Are the split membership lists, prepared structure files or checksums, and per-complex predictions used for the reported tables available? These would help us distinguish data preparation and sample differences from implementation differences.

We recognize that some of these materials may no longer be available. Any clarification you can provide would be very helpful. We would be happy to share our scripts and comparisons.

Best regards,

Smriti Pradhan
