# Adversarial Attack Description: CA-16 — Colloquial

## 1. Metadata

| Field | Value |
|---|---|
| Attack ID | CA-16 |
| Attack Name | Colloquial |
| Category | claim_attack |
| Attack Target | disrupted_retrieval |
| Edit Granularity | sentence |
| Strategy Type | lm_based |
| Access Assumption | Black-box |
| Source Paper | Kim et al., 2021, Sec. 5.1.1 |

## 2. Description
This attack rephrases a formal, evidence-style claim into casual, everyday spoken language. The meaning stays the same, but the wording drifts far enough from the formal evidence text that keyword/embedding-based retrieval systems struggle to match the claim to its correct evidence document.

## 3. Preconditions / Required Inputs
Original formal claim text (required); a generative/paraphrasing model that supports your language and can shift register toward informal speech (required).

## 4. Procedure
1. Take the original formal claim (typically drawn from an official/news register).
2. Prompt a generative model to rephrase it in casual, conversational language, including everyday vocabulary and any code-mixing common in spoken usage of your language.
3. Confirm the informal version preserves the original factual meaning.
4. Measure retrieval performance (document/evidence recall) on the informal version versus the original.

## 5. Output Schema (JSON)
```json
{ "attack_id": "CA-16", "language": "<ISO code: hi | mni | te | ur | pa | ta | or | ml>", "original_claim": "...", "original_evidence": null, "adversarial_claim": "...", "adversarial_evidence": null, "gold_label": "SUP | REF | NEI", "target_label": "SUP | REF | NEI | same_as_gold", "edit_granularity": "sentence", "technique_params": { "attack_name": "Colloquial" }, "validity_flags": { "fluency_checked": true, "label_consistent": true, "meaning_preserved": true } }
```

## 6A. Implementation Notes *(input — engineering constraints only, no claims about effectiveness)*
Check whether informal/spoken registers in your language commonly mix in loanwords or code-switch with another language (common in many South Asian languages when discussing government/technical topics) — if so, this attack can be extended into a code-mixed retrieval-robustness variant, which is a genuinely interesting language-specific stress test with no fixed English-only equivalent.

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
| Claim / Evidence | The government has launched a new scheme to ensure the availability of health services in rural areas. | Govt started a new scheme so villages can get proper health services now. |
| Label (gold → target) | gold label | Disrupted retrieval (formal evidence text doesn't lexically match casual/code-mixed claim wording) |
| Language | <your language> | <your language> |

## 9. Failure Modes / Skip Conditions
Skip if the generation model produces disfluent or unnatural colloquial output in your language — verify fluency before including in the evaluation set.
