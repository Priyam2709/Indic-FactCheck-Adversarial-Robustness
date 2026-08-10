# Adversarial Attack Description: CA-14 — Multi-hop

## 1. Metadata

| Field | Value |
|---|---|
| Attack ID | CA-14 |
| Attack Name | Multi-hop |
| Category | claim_attack |
| Attack Target | disrupted_retrieval |
| Edit Granularity | sentence |
| Strategy Type | rule_based |
| Access Assumption | Black-box |
| Source Paper | Hidey et al., 2020, Sec. 5.1.1 |

## 2. Description
This attack builds claims that can only be verified by combining information from two or more separate evidence articles (not just one). Since most retrieval systems are tuned to find one strong matching document, multi-hop claims often cause the retriever to only find part of the needed evidence, leading to an incomplete or wrong verdict.

## 3. Preconditions / Required Inputs
Two or more evidence articles connected by a shared entity (required, e.g., the same department, scheme, or person appearing in both); a way to verify the claim is only true when both pieces are combined (required).

## 4. Procedure
1. Select two evidence articles sharing a common entity (e.g., an official mentioned in both a scheme-launch article and a budget-allocation article).
2. Construct a claim that requires facts from both articles to fully verify (e.g., linking who launched a scheme with its exact funding figure from a separate document).
3. Confirm that no single article alone provides enough evidence for a correct verdict.
4. Label the claim based on the combined evidence, and log both required source documents.

## 5. Output Schema (JSON)
```json
{ "attack_id": "CA-14", "language": "<ISO code: hi | mni | te | ur | pa | ta | or | ml>", "original_claim": "...", "original_evidence": null, "adversarial_claim": "...", "adversarial_evidence": null, "gold_label": "SUP | REF | NEI", "target_label": "SUP | REF | NEI | same_as_gold", "edit_granularity": "sentence", "technique_params": { "attack_name": "Multi-hop" }, "validity_flags": { "fluency_checked": true, "label_consistent": true, "meaning_preserved": true } }
```

## 6A. Implementation Notes *(input — engineering constraints only, no claims about effectiveness)*
Requires your evidence repository to have genuine cross-document links (shared entities across multiple source documents in your language) — this requirement is the same regardless of which language you're working in. If your dataset spans multiple domains (e.g., Politics + Healthcare), cross-domain multi-hop claims are a natural, realistic option.

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
| Claim / Evidence | (Doc A: Health department announces a new scheme; Doc B: Finance department approves a 3,000 crore rupee budget for it) | The new health scheme was approved a budget of 3,000 crore rupees by the finance department. |
| Label (gold → target) | gold label | Disrupted retrieval (single-document retriever likely finds only Doc A or B, not both) |
| Language | <your language> | <your language> |

## 9. Failure Modes / Skip Conditions
Skip if no two evidence articles in the corpus share a linking entity, since there's no genuine multi-hop relationship to exploit.
