# Adversarial Attack Description: CA-01 — Model-targeting

## 1. Metadata

| Field | Value |
|---|---|
| Attack ID | CA-01 |
| Attack Name | Model-targeting |
| Category | claim_attack |
| Attack Target | corrupted_verdict |
| Edit Granularity | sentence |
| Strategy Type | rule_based |
| Access Assumption | White-box for the model it targets (e.g., NSMN); black-box for others |
| Source Paper | Thorne et al., 2019a, Sec. 5.1.1 |

## 2. Description
This attack rewrites a claim into a different sentence that means the same thing, but is specifically engineered using a fact-checking model's own predictions as a guide. It uses a technique called SEARs (Semantically Equivalent Adversarial Rules) — a set of rewrite patterns that shouldn't change a claim's truth value, but happen to confuse the model into flipping its verdict.

## 3. Preconditions / Required Inputs
Original claim text (required); gold label (required); access to the target verifier's prediction scores for candidate rewrites (required — this is what makes it 'model-targeting' rather than generic paraphrasing).

## 4. Procedure
1. Take the original claim and generate a pool of candidate rewrites using safe, meaning-preserving transformation rules (e.g., reordering clauses, swapping active/passive voice).
2. Feed each candidate through the target verification model and record its predicted label.
3. Select the candidate whose meaning is preserved (per human or LM check) but whose predicted label differs from the gold label.
4. Log the original claim, the selected adversarial claim, and the verdict flip achieved.

## 5. Output Schema (JSON)
```json
{ "attack_id": "CA-01", "language": "<ISO code: hi | mni | te | ur | pa | ta | or | ml>", "original_claim": "...", "original_evidence": null, "adversarial_claim": "...", "adversarial_evidence": null, "gold_label": "SUP | REF | NEI", "target_label": "SUP | REF | NEI | same_as_gold", "edit_granularity": "sentence", "technique_params": { "attack_name": "Model-targeting" }, "validity_flags": { "fluency_checked": true, "label_consistent": true, "meaning_preserved": true } }
```

## 6A. Implementation Notes *(input — engineering constraints only, no claims about effectiveness)*
How feasible clause-reordering is depends heavily on your language's word-order flexibility. Free-word-order languages (e.g., Hindi, Urdu, Tamil, Telugu — all allow more reordering than English) make this attack easier to generate but require extra care that reordering doesn't change emphasis or introduce ambiguity. Fixed-word-order languages will need alternative rewrite strategies (e.g., voice change, clause fronting) instead of relying on reordering alone.

| Language | Script | Execution Blockers / Requirements (tooling only) |
|---|---|---|
| Hindi | Devanagari | (fill in per attack) |
| Manipuri | Meitei Mayek / Bengali (varies by corpus) | (fill in per attack) |
| Telugu | Telugu | (fill in per attack) |
| Urdu | Perso-Arabic (RTL) | (fill in per attack) |
| Punjabi | Gurmukhi | (fill in per attack) |
| Tamil | Tamil | (fill in per attack) |
| Odia | Odia | (fill in per attack) |
| Malayalam | Malayalam | (fill in per attack) |

## 6B. Empirical Outcome *(output — left blank in the template; filled in by the evaluation pipeline after the attack is run, not assumed in advance)*
```json
{ "language": "<ISO code>", "attack_executed": null, "execution_notes": null, "verdict_flipped": null, "retrieval_disrupted": null, "fluency_score": null, "human_detectability": null, "attack_success_rate": null, "notes": "To be filled in after running this attack against your trained baseline model." }
```

## 7. Success / Validity Criteria
An instance is usable for evaluation if: (a) meaning is preserved relative to the original claim unless the attack explicitly targets meaning drift, (b) the claim is fluent, natural text in your target language as judged by a native reader, (c) the assigned gold/target label is correct given the evidence, and (d) the failure mode (verdict flip vs. retrieval disruption) matches the Attack Target above. Report using survey metrics from Appendix C.2 where applicable: Potency, Correctness Rate, Resilience (for corrupted_verdict attacks) or Evidence/Document Recall (for disrupted_retrieval attacks).

## 8. Example
*Example shown in English for language-neutral illustration — translate the same pattern into your assigned language.*

| Field | Original | Adversarial |
|---|---|---|
| Claim / Evidence | The Election Commission gave home-voting facility to elderly voters above 85 years of age. | Home-voting facility was given to voters above 85 years of age by the Election Commission. |
| Label (gold → target) | gold label | SUP → REF (if the model is confused by the reordered subject–object structure) |
| Language | <your language> | <your language> |

## 9. Failure Modes / Skip Conditions
Skip if the claim has fewer than 6 words (too short to safely reorder without changing meaning), or if no model access is available to test candidate rewrites.
