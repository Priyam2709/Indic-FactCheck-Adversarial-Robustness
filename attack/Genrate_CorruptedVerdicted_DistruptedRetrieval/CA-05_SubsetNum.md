# Adversarial Attack Description: CA-05 — SubsetNum

## 1. Metadata

| Field | Value |
|---|---|
| Attack ID | CA-05 |
| Attack Name | SubsetNum |
| Category | claim_attack |
| Attack Target | corrupted_verdict |
| Edit Granularity | sentence |
| Strategy Type | rule_based |
| Access Assumption | Black-box |
| Source Paper | Kim and Allan, 2019, Sec. 5.1.1 |

## 2. Description
This attack exploits reasoning about parts and wholes. It generates claims that require the model to understand subset relationships between entities (e.g., a claim about 'some states' when the evidence talks about 'all states', or vice versa) — a subtle numerical/logical distinction that surface-pattern-matching models tend to miss entirely.

## 3. Preconditions / Required Inputs
Evidence containing a quantified or enumerated set (required, e.g., a list of states, ministries, or categories); gold label SUPPORTED (required — this attack always starts from SUP-origin claims).

## 4. Procedure
1. Identify evidence containing a specific count, list, or quantified group (e.g., 'in 18 states').
2. Generate a claim that asserts a subset or superset relationship inconsistent with the exact evidence (e.g., claiming 'in all states' when evidence only lists a partial set).
3. Label the claim NEI, since the evidence doesn't fully support the broader/narrower claim as stated.
4. Log the specific quantifier substitution used, for later analysis of which quantifier types are most disruptive.

## 5. Output Schema (JSON)
```json
{ "attack_id": "CA-05", "language": "<ISO code: hi | mni | te | ur | pa | ta | or | ml>", "original_claim": "...", "original_evidence": null, "adversarial_claim": "...", "adversarial_evidence": null, "gold_label": "SUP | REF | NEI", "target_label": "SUP | REF | NEI | same_as_gold", "edit_granularity": "sentence", "technique_params": { "attack_name": "SubsetNum" }, "validity_flags": { "fluency_checked": true, "label_consistent": true, "meaning_preserved": true } }
```

## 6A. Implementation Notes *(input — engineering constraints only, no claims about effectiveness)*
Quantifier words (all/some/most/several) exist in some form in every language and generally map fairly directly across languages, so this attack transfers with little adaptation. The main requirement is a model or annotator that can reliably tag numeric or enumerated evidence in your target language's text.

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
| Claim / Evidence | Digital payment infrastructure was expanded in 18 states. | Digital payment infrastructure was expanded in all states. |
| Label (gold → target) | gold label | SUP → NEI (evidence only supports a partial list, not a universal claim) |
| Language | <your language> | <your language> |

## 9. Failure Modes / Skip Conditions
Skip if the evidence contains no numeric, listed, or otherwise quantifiable set to build the subset distinction from.
