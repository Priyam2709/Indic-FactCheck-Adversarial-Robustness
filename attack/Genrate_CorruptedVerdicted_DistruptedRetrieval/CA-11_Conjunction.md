# Adversarial Attack Description: CA-11 — Conjunction

## 1. Metadata

| Field | Value |
|---|---|
| Attack ID | CA-11 |
| Attack Name | Conjunction |
| Category | claim_attack |
| Attack Target | corrupted_verdict |
| Edit Granularity | sentence |
| Strategy Type | rule_based |
| Access Assumption | Black-box |
| Source Paper | Hidey et al., 2020, Sec. 5.1.1 |

## 2. Description
This attack builds compound claims by joining two separate factual clauses (using 'and') that both come from the same evidence document. It tests whether the model verifies the whole compound claim correctly, or only checks one clause and misses that the other part is false or unsupported.

## 3. Preconditions / Required Inputs
A single evidence document containing at least two distinct, checkable facts (required); gold labels for each individual clause (required).

## 4. Procedure
1. Identify two separate factual statements within one evidence article.
2. Join them into a single claim using a conjunction in your language (equivalent of 'and'/'as well as').
3. Deliberately make one clause true (per evidence) and the other false or unverifiable.
4. Label the compound claim REFUTED or NEI depending on which clause fails, and log which clause was the 'trap'.

## 5. Output Schema (JSON)
```json
{ "attack_id": "CA-11", "language": "<ISO code: hi | mni | te | ur | pa | ta | or | ml>", "original_claim": "...", "original_evidence": null, "adversarial_claim": "...", "adversarial_evidence": null, "gold_label": "SUP | REF | NEI", "target_label": "SUP | REF | NEI | same_as_gold", "edit_granularity": "sentence", "technique_params": { "attack_name": "Conjunction" }, "validity_flags": { "fluency_checked": true, "label_consistent": true, "meaning_preserved": true } }
```

## 6A. Implementation Notes *(input — engineering constraints only, no claims about effectiveness)*
Conjunctions work very similarly across most languages, so this attack transfers with almost no adaptation. The main requirement is simply having evidence documents rich enough to contain two distinct checkable facts.

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
| Claim / Evidence | (Evidence: scheme launched in 2022 with a 2,000 crore rupee budget, covering 12 states) | The scheme launched in 2022 and covered 20 states. |
| Label (gold → target) | gold label | REF (first clause true, second clause false — 20 states vs. actual 12) |
| Language | <your language> | <your language> |

## 9. Failure Modes / Skip Conditions
Skip if the source evidence document contains only one checkable fact, since there's no second clause to attach.
