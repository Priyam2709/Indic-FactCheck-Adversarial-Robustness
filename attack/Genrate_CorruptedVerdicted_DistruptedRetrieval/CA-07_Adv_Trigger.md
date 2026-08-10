# Adversarial Attack Description: CA-07 — Adv. Trigger

## 1. Metadata

| Field | Value |
|---|---|
| Attack ID | CA-07 |
| Attack Name | Adv. Trigger |
| Category | claim_attack |
| Attack Target | corrupted_verdict |
| Edit Granularity | sentence |
| Strategy Type | lm_based |
| Access Assumption | White-box (needs gradient/embedding access for trigger optimization) |
| Source Paper | Atanasova et al., 2020, Sec. 5.1.1 |

## 2. Description
This is a more technical attack: it finds a short sequence of words (a 'trigger') that, when prepended to a claim, flips the model's verdict with minimal disruption to grammar or meaning. The trigger is found through an optimization process (originally HotFlip) that searches for the token sequence causing maximum confusion.

## 3. Preconditions / Required Inputs
White-box access to the target model's embeddings/gradients (required); a semantic similarity model in your language to filter triggers that don't distort meaning too much (required).

## 4. Procedure
1. Initialize a random short token sequence in your language as the candidate trigger.
2. Use gradient-based search (HotFlip-style) against the target model to iteratively replace tokens in the trigger, aiming to flip the predicted label.
3. Filter candidate triggers using a semantic similarity model, keeping only those that don't drastically alter the claim's apparent meaning.
4. Prepend the optimized trigger to the original claim to form the adversarial claim.

## 5. Output Schema (JSON)
```json
{ "attack_id": "CA-07", "language": "<ISO code: hi | mni | te | ur | pa | ta | or | ml>", "original_claim": "...", "original_evidence": null, "adversarial_claim": "...", "adversarial_evidence": null, "gold_label": "SUP | REF | NEI", "target_label": "SUP | REF | NEI | same_as_gold", "edit_granularity": "sentence", "technique_params": { "attack_name": "Adv. Trigger" }, "validity_flags": { "fluency_checked": true, "label_consistent": true, "meaning_preserved": true } }
```

## 6A. Implementation Notes *(input — engineering constraints only, no claims about effectiveness)*
The gradient-based search technique is language-agnostic in principle (it operates on token embeddings), but requires a tokenizer/embedding space from the *same* target model being attacked in your language, plus a semantic-similarity scorer for the filtering step. This is the most tooling-heavy attack in this set to build for any language, and may need to be deprioritized if these components aren't available.

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
| Claim / Evidence | The government announced an increase in the minimum support price. | actually the real fact the government announced an increase in the minimum support price. |
| Label (gold → target) | gold label | SUP → REF (illustrative; actual trigger tokens must come from optimization, not hand-picking) |
| Language | <your language> | <your language> |

## 9. Failure Modes / Skip Conditions
Skip entirely if white-box gradient access to the target model is unavailable — this attack cannot be approximated in a black-box setting without losing its defining mechanism.
