# Adversarial Attack Description: CA-02 — Dataset Bias

## 1. Metadata

| Field | Value |
|---|---|
| Attack ID | CA-02 |
| Attack Name | Dataset Bias |
| Category | claim_attack |
| Attack Target | corrupted_verdict |
| Edit Granularity | sentence |
| Strategy Type | rule_based |
| Access Assumption | Black-box |
| Source Paper | Thorne et al., 2019a, Sec. 5.1.1 |

## 2. Description
Rather than attacking a specific model, this attack exploits a weakness in how the training dataset itself was built. It creates claims using patterns — like simple or complex negations, or entailment-preserving rewrites — that are statistically rare or oddly distributed in the original dataset, so models that memorized surface patterns (instead of learning real reasoning) get fooled.

## 3. Preconditions / Required Inputs
Original claim text (required); gold label (required); knowledge of common negation/rewrite patterns underrepresented in the training data (required).

## 4. Procedure
1. Identify negation-style transformations: simple negation (add/remove a negation word), complex negation (rephrase using an antonym instead of a negation word), and entailment-preserving rewrites.
2. Apply one transformation type to the claim while keeping the evidence unchanged.
3. Verify the new claim still logically matches the intended gold label (a human or LM check is required, since the rewrite itself may accidentally change the true label).
4. Record the transformed claim and its transformation type.

## 5. Output Schema (JSON)
```json
{ "attack_id": "CA-02", "language": "<ISO code: hi | mni | te | ur | pa | ta | or | ml>", "original_claim": "...", "original_evidence": null, "adversarial_claim": "...", "adversarial_evidence": null, "gold_label": "SUP | REF | NEI", "target_label": "SUP | REF | NEI | same_as_gold", "edit_granularity": "sentence", "technique_params": { "attack_name": "Dataset Bias" }, "validity_flags": { "fluency_checked": true, "label_consistent": true, "meaning_preserved": true } }
```

## 6A. Implementation Notes *(input — engineering constraints only, no claims about effectiveness)*
Check how your language expresses negation — some languages have a single general negation particle, others (Hindi/Urdu, for example) vary the negation word by mood and tense. Complex/antonym-based negation depends on your language having natural antonym pairs for common verbs/adjectives — confirm a lexical resource or native-speaker judgment is available before relying on this.

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
| Claim / Evidence | The government has fully implemented the new education policy. | The government has left the new education policy incomplete. |
| Label (gold → target) | gold label | SUP → REF (antonym-based complex negation, same underlying fact reworded) |
| Language | <your language> | <your language> |

## 9. Failure Modes / Skip Conditions
Skip if the claim contains no verb or property that has a natural antonym in your language.
