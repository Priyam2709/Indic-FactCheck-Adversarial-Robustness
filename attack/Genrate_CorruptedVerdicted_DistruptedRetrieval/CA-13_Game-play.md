# Adversarial Attack Description: CA-13 — Game-play

## 1. Metadata

| Field | Value |
|---|---|
| Attack ID | CA-13 |
| Attack Name | Game-play |
| Category | claim_attack |
| Attack Target | corrupted_verdict |
| Edit Granularity | sentence |
| Strategy Type | rule_based |
| Access Assumption | Black-box |
| Source Paper | Eisenschlos et al., 2021, Sec. 5.1.1 |

## 2. Description
Unlike the automated attacks above, this one is human-generated: two people play a competitive game where one writes tricky-but-fair claims and the other tries to fact-check them, continuing until claims are genuinely hard for AI systems but still clearly correct/incorrect to a human. It produces higher-quality, more natural adversarial claims than most rule-based methods.

## 3. Preconditions / Required Inputs
Two human annotators fluent in your target language (required); an evidence document as the shared reference (required); a scoring/incentive structure to keep claims genuinely difficult but fair (recommended).

## 4. Procedure
1. Pair two fluent speakers of your language: a 'claim writer' and a 'verifier'.
2. Give the claim writer an evidence document and ask them to write a claim designed to be hard for an AI model but clearly verifiable by a human reader.
3. Have the verifier attempt to fact-check the claim without seeing the writer's intended answer.
4. Keep only claims both annotators agree on the correct label for, to ensure label quality despite the adversarial framing.

## 5. Output Schema (JSON)
```json
{ "attack_id": "CA-13", "language": "<ISO code: hi | mni | te | ur | pa | ta | or | ml>", "original_claim": "...", "original_evidence": null, "adversarial_claim": "...", "adversarial_evidence": null, "gold_label": "SUP | REF | NEI", "target_label": "SUP | REF | NEI | same_as_gold", "edit_granularity": "sentence", "technique_params": { "attack_name": "Game-play" }, "validity_flags": { "fluency_checked": true, "label_consistent": true, "meaning_preserved": true } }
```

## 6A. Implementation Notes *(input — engineering constraints only, no claims about effectiveness)*
This attack is entirely dependent on having fluent human annotators in your language (ideally 2+ people, possibly project teammates) — it needs no NLP tooling at all, making it one of the most reliably executable attacks for any of the 8 project languages, though it is the most time-intensive per example.

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
| Claim / Evidence | (Evidence: official press release on a housing scheme) | (Human-written claim deliberately using indirect phrasing/implication rather than restating evidence directly — exact wording depends on the annotator pair and language) |
| Label (gold → target) | gold label | Varies (human-crafted, not template-generated) |
| Language | <your language> | <your language> |

## 9. Failure Modes / Skip Conditions
Skip if only one annotator is available — the adversarial quality of this method depends on the writer/verifier dynamic between two independent people.
