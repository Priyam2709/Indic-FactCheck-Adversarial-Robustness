# Adversarial Attack Description: CA-12 — Add. Unver.

## 1. Metadata

| Field | Value |
|---|---|
| Attack ID | CA-12 |
| Attack Name | Add. Unver. |
| Category | claim_attack |
| Attack Target | corrupted_verdict |
| Edit Granularity | sentence |
| Strategy Type | rule_based |
| Access Assumption | Black-box |
| Source Paper | Hidey et al., 2020, Sec. 5.1.1 |

## 2. Description
Similar in spirit to Conjunction, this attack takes an otherwise NEI claim and adds an extra, unverifiable proposition to it. The added part can't be checked against any evidence at all, which should keep the claim NEI — but models sometimes latch onto the verifiable part and wrongly output SUP or REF.

## 3. Preconditions / Required Inputs
An NEI-origin claim (required); an additional proposition with no corresponding evidence in the corpus (required).

## 4. Procedure
1. Start from a claim already labeled NEI.
2. Append an additional statement that is plausible-sounding but has no evidence anywhere in the corpus (e.g., an opinion, a future prediction, or an unrecorded detail).
3. Confirm the added proposition truly has no matching evidence.
4. Keep the gold label as NEI, and log the added proposition type for analysis.

## 5. Output Schema (JSON)
```json
{ "attack_id": "CA-12", "language": "<ISO code: hi | mni | te | ur | pa | ta | or | ml>", "original_claim": "...", "original_evidence": null, "adversarial_claim": "...", "adversarial_evidence": null, "gold_label": "SUP | REF | NEI", "target_label": "SUP | REF | NEI | same_as_gold", "edit_granularity": "sentence", "technique_params": { "attack_name": "Add. Unver." }, "validity_flags": { "fluency_checked": true, "label_consistent": true, "meaning_preserved": true } }
```

## 6A. Implementation Notes *(input — engineering constraints only, no claims about effectiveness)*
No special language tooling required — this is a compositional attack, meaning the difficulty is entirely in careful corpus-checking (confirming true absence of evidence), not in any language-specific processing. Applies identically across all project languages.

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
| Claim / Evidence | The scheme's benefits will reach families in rural areas. | The scheme's benefits will reach families in rural areas, and experts say it will influence the outcome of the next election. |
| Label (gold → target) | gold label | NEI (unchanged — added political-prediction clause has no evidence, model may still guess SUP) |
| Language | <your language> | <your language> |

## 9. Failure Modes / Skip Conditions
Skip if you cannot confidently confirm the added proposition has zero supporting evidence anywhere in the corpus.
