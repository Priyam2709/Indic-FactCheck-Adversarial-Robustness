# Adversarial Attack Description: CA-10 — NotEnoughInfo Add

## 1. Metadata

| Field | Value |
|---|---|
| Attack ID | CA-10 |
| Attack Name | NotEnoughInfo Add |
| Category | claim_attack |
| Attack Target | corrupted_verdict |
| Edit Granularity | sentence |
| Strategy Type | rule_based |
| Access Assumption | Black-box |
| Source Paper | Kim and Allan, 2019, Sec. 5.1.1 |

## 2. Description
This is a simpler, dataset-balancing style attack: it deliberately adds more NEI-labeled claims to the dataset so that models can't just learn to guess SUPPORTED or REFUTED as a shortcut when they're unsure. It stress-tests whether the model can genuinely recognize insufficient evidence.

## 3. Preconditions / Required Inputs
A claim with no matching evidence document currently in the repository (required, or evidence deliberately withheld); gold label NEI (required).

## 4. Procedure
1. Select or write a claim about a real topic for which no evidence document currently exists in the evaluation corpus.
2. Confirm no partial-match evidence accidentally exists that could make the claim verifiable.
3. Label the claim NEI and add it to the evaluation set.
4. Track the ratio of NEI additions relative to SUP/REF claims to maintain a target class balance.

## 5. Output Schema (JSON)
```json
{ "attack_id": "CA-10", "language": "<ISO code: hi | mni | te | ur | pa | ta | or | ml>", "original_claim": "...", "original_evidence": null, "adversarial_claim": "...", "adversarial_evidence": null, "gold_label": "SUP | REF | NEI", "target_label": "SUP | REF | NEI | same_as_gold", "edit_granularity": "sentence", "technique_params": { "attack_name": "NotEnoughInfo Add" }, "validity_flags": { "fluency_checked": true, "label_consistent": true, "meaning_preserved": true } }
```

## 6A. Implementation Notes *(input — engineering constraints only, no claims about effectiveness)*
This is one of the most straightforward attacks to build in any language — it requires no linguistic tooling at all, only careful bookkeeping of your evidence repository to confirm genuine absence of supporting evidence.

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
| Claim / Evidence | (N/A — this attack authors new claims rather than modifying existing ones) | The state government made the digital health records scheme mandatory statewide starting in 2025. |
| Label (gold → target) | gold label | N/A → NEI (no evidence exists in the corpus for this claim) |
| Language | <your language> | <your language> |

## 9. Failure Modes / Skip Conditions
Skip if you cannot confirm the absence of matching evidence with reasonable confidence — an accidental false NEI label undermines dataset quality.
