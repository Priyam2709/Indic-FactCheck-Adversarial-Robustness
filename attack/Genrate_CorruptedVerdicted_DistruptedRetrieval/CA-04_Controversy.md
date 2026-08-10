# Adversarial Attack Description: CA-04 — Controversy

## 1. Metadata

| Field | Value |
|---|---|
| Attack ID | CA-04 |
| Attack Name | Controversy |
| Category | claim_attack |
| Attack Target | corrupted_verdict |
| Edit Granularity | sentence |
| Strategy Type | rule_based |
| Access Assumption | Black-box |
| Source Paper | Kim and Allan, 2019, Sec. 5.1.1 |

## 2. Description
This attack manufactures REFUTED claims out of situations where two evidence sentences actually contradict each other. It deliberately picks the 'losing' or minority side of a real disagreement in the source material, producing a claim that looks well-evidenced on the surface but is built on a genuinely contested fact.

## 3. Preconditions / Required Inputs
A pair of evidence sentences that contradict each other on the same topic (required); gold label REFUTED (required — this attack always targets REF-origin claims).

## 4. Procedure
1. Search the evidence repository for two sentences about the same entity/event that state conflicting facts.
2. Construct a claim asserting the version supported by only one of the two sentences.
3. Label the claim REFUTED, since the other, contradicting evidence sentence exists in the corpus.
4. Store both evidence sentences for downstream retrieval-based evaluation.

## 5. Output Schema (JSON)
```json
{ "attack_id": "CA-04", "language": "<ISO code: hi | mni | te | ur | pa | ta | or | ml>", "original_claim": "...", "original_evidence": null, "adversarial_claim": "...", "adversarial_evidence": null, "gold_label": "SUP | REF | NEI", "target_label": "SUP | REF | NEI | same_as_gold", "edit_granularity": "sentence", "technique_params": { "attack_name": "Controversy" }, "validity_flags": { "fluency_checked": true, "label_consistent": true, "meaning_preserved": true } }
```

## 6A. Implementation Notes *(input — engineering constraints only, no claims about effectiveness)*
Needs a source corpus in your language large enough to contain naturally occurring contradictions (e.g., differing official statements, or news that revises earlier figures). With a small hand-curated dataset (a few hundred rows), contradictory pairs will likely need to be manually seeded rather than mined automatically, regardless of language.

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
| Claim / Evidence | 10,000 crore rupees have been disbursed under the scheme so far. | (Claim asserts an older/superseded figure while a separate, newer evidence sentence states an updated, different figure) |
| Label (gold → target) | gold label | REF → SUP (model may pick the first matching number without checking for a contradicting, more recent figure) |
| Language | <your language> | <your language> |

## 9. Failure Modes / Skip Conditions
Skip if no genuinely contradictory evidence pair exists in the corpus for a given topic — do not fabricate a contradiction that isn't grounded in real source material.
