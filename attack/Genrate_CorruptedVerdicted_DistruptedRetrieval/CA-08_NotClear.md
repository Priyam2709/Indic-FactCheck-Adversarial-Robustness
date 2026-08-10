# Adversarial Attack Description: CA-08 — NotClear

## 1. Metadata

| Field | Value |
|---|---|
| Attack ID | CA-08 |
| Attack Name | NotClear |
| Category | claim_attack |
| Attack Target | corrupted_verdict |
| Edit Granularity | sentence |
| Strategy Type | rule_based |
| Access Assumption | Black-box |
| Source Paper | Kim and Allan, 2019, Sec. 5.1.1 |

## 2. Description
This attack builds NEI (Not Enough Info) claims directly from evidence sentences that themselves contain hedging or uncertainty language (like 'it is not clear'). It tests whether the model can correctly recognize genuine evidentiary uncertainty rather than forcing a SUP or REF guess.

## 3. Preconditions / Required Inputs
Evidence sentence containing explicit hedging/uncertainty language (required); gold label NEI (required — this attack always targets NEI-origin claims).

## 4. Procedure
1. Search the evidence corpus for sentences containing hedge markers in your language (equivalents of 'not clear', 'estimated', 'possibly').
2. Construct a claim that asserts the hedged statement as if it were a settled fact.
3. Label the claim NEI, since the source evidence explicitly signals uncertainty.
4. Record which hedge marker was used, to analyze which uncertainty phrases are hardest for the model to catch.

## 5. Output Schema (JSON)
```json
{ "attack_id": "CA-08", "language": "<ISO code: hi | mni | te | ur | pa | ta | or | ml>", "original_claim": "...", "original_evidence": null, "adversarial_claim": "...", "adversarial_evidence": null, "gold_label": "SUP | REF | NEI", "target_label": "SUP | REF | NEI | same_as_gold", "edit_granularity": "sentence", "technique_params": { "attack_name": "NotClear" }, "validity_flags": { "fluency_checked": true, "label_consistent": true, "meaning_preserved": true } }
```

## 6A. Implementation Notes *(input — engineering constraints only, no claims about effectiveness)*
Every language has hedging/uncertainty expressions in formal register (news, official text) — a small manually-built list of hedge phrases in your language is enough to start with; no special NLP tooling is required beyond simple keyword search.

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
| Claim / Evidence | The exact impact of the scheme is not yet clear. | The exact impact of the scheme has been proven. |
| Label (gold → target) | gold label | NEI → SUP (claim overstates certainty that evidence explicitly withholds) |
| Language | <your language> | <your language> |

## 9. Failure Modes / Skip Conditions
Skip if no hedge-marker sentence exists in the available evidence for a given topic.
