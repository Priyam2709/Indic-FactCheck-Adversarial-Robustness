# Adversarial Attack Description: CA-09 — FiniteSet

## 1. Metadata

| Field | Value |
|---|---|
| Attack ID | CA-09 |
| Attack Name | FiniteSet |
| Category | claim_attack |
| Attack Target | corrupted_verdict |
| Edit Granularity | sentence |
| Strategy Type | rule_based |
| Access Assumption | Black-box |
| Source Paper | Kim and Allan, 2019, Sec. 5.1.1 |

## 2. Description
This attack targets time-sensitive facts. It generates claims about events or figures that were only true within a specific, finite time window, then asks the model to verify them without any temporal context — testing whether the model naively verifies a once-true-now-outdated fact.

## 3. Preconditions / Required Inputs
Evidence containing a date or time-bound fact (required); gold label SUPPORTED or REFUTED with a known validity window (required).

## 4. Procedure
1. Identify evidence with a clearly time-bound fact (e.g., a scheme's initial budget before a later revision).
2. Strip or obscure the temporal qualifier from the claim, presenting the fact as if permanently true.
3. Label the claim NEI, since verifying it correctly now requires temporal reasoning the model likely lacks.
4. Log the original time window for later temporal-reasoning-specific analysis.

## 5. Output Schema (JSON)
```json
{ "attack_id": "CA-09", "language": "<ISO code: hi | mni | te | ur | pa | ta | or | ml>", "original_claim": "...", "original_evidence": null, "adversarial_claim": "...", "adversarial_evidence": null, "gold_label": "SUP | REF | NEI", "target_label": "SUP | REF | NEI | same_as_gold", "edit_granularity": "sentence", "technique_params": { "attack_name": "FiniteSet" }, "validity_flags": { "fluency_checked": true, "label_consistent": true, "meaning_preserved": true } }
```

## 6A. Implementation Notes *(input — engineering constraints only, no claims about effectiveness)*
Check how dates and numbers are written in your language — many South Asian languages allow a native script numeral system, Latin numerals, and fully spelled-out number words all in the same corpus. Any date-detection step must handle all forms actually present in your data, not just one.

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
| Claim / Evidence | In 2021, the scheme's budget was 5,000 crore rupees. | The scheme's budget is 5,000 crore rupees. |
| Label (gold → target) | gold label | SUP → NEI (claim drops the year, but the budget figure has since changed) |
| Language | <your language> | <your language> |

## 9. Failure Modes / Skip Conditions
Skip if the evidence contains no explicit date/time marker to strip, since the attack depends on removing a genuine temporal qualifier.
