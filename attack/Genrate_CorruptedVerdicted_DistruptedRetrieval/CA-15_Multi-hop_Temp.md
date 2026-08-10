# Adversarial Attack Description: CA-15 — Multi-hop Temp.

## 1. Metadata

| Field | Value |
|---|---|
| Attack ID | CA-15 |
| Attack Name | Multi-hop Temp. |
| Category | claim_attack |
| Attack Target | disrupted_retrieval |
| Edit Granularity | sentence |
| Strategy Type | rule_based |
| Access Assumption | Black-box |
| Source Paper | Hidey et al., 2020, Sec. 5.1.1 |

## 2. Description
A variant of Multi-hop that specifically links entities using temporal relationships across different evidence articles (e.g., 'the scheme launched before the policy that replaced it'). This adds a reasoning-over-time dimension on top of the cross-document retrieval challenge.

## 3. Preconditions / Required Inputs
Two or more evidence articles with explicit or inferable dates (required); a genuine temporal relationship connecting them (required, e.g., 'launched before', 'revised after').

## 4. Procedure
1. Select two evidence articles about related events with known dates.
2. Construct a claim asserting the temporal relationship between them (before/after/during).
3. Confirm the temporal relationship truly requires cross-referencing both documents' dates.
4. Label the claim based on whether the asserted temporal order is correct, and log both source dates.

## 5. Output Schema (JSON)
```json
{ "attack_id": "CA-15", "language": "<ISO code: hi | mni | te | ur | pa | ta | or | ml>", "original_claim": "...", "original_evidence": null, "adversarial_claim": "...", "adversarial_evidence": null, "gold_label": "SUP | REF | NEI", "target_label": "SUP | REF | NEI | same_as_gold", "edit_granularity": "sentence", "technique_params": { "attack_name": "Multi-hop Temp." }, "validity_flags": { "fluency_checked": true, "label_consistent": true, "meaning_preserved": true } }
```

## 6A. Implementation Notes *(input — engineering constraints only, no claims about effectiveness)*
Same date-format complexity as FiniteSet applies here (native script numerals, Latin numerals, spelled-out forms — check which appear in your corpus) — plus this attack additionally needs reliable date *comparison* logic, not just date detection.

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
| Claim / Evidence | (Doc A, dated 2022: old scheme launched; Doc B, dated 2024: scheme revised with new eligibility criteria) | The eligibility criteria were revised before the scheme was launched. |
| Label (gold → target) | gold label | REF, but disrupted retrieval likely surfaces only one dated document, not both |
| Language | <your language> | <your language> |

## 9. Failure Modes / Skip Conditions
Skip if evidence articles lack explicit or reliably inferable dates.
