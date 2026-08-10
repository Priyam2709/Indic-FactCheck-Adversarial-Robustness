# Adversarial Attack Description: CA-06 — Fact Mixing

## 1. Metadata

| Field | Value |
|---|---|
| Attack ID | CA-06 |
| Attack Name | Fact Mixing |
| Category | claim_attack |
| Attack Target | corrupted_verdict |
| Edit Granularity | sentence |
| Strategy Type | lm_based |
| Access Assumption | Black-box |
| Source Paper | Niewinski et al., 2019, Sec. 5.1.1 |

## 2. Description
Using a controlled text-generation model (originally GPT-2), this attack blends facts pulled from multiple different evidence articles into a single, fluent-sounding claim. The result reads naturally and doesn't break grammar rules, but conflates information from unrelated sources in a way that misleads verification.

## 3. Preconditions / Required Inputs
Two or more evidence articles on related but distinct topics (required); a generative language model that supports your language (required).

## 4. Procedure
1. Select two evidence articles that share an entity or theme (e.g., two different government schemes under the same ministry).
2. Prompt a generative model in your language to produce a single claim that blends a fact from each article while remaining grammatically fluent.
3. Check the generated claim doesn't literally copy either source sentence (to preserve novelty).
4. Assign label based on whether the blended claim is actually verifiable against either single source (usually NEI or REF).

## 5. Output Schema (JSON)
```json
{ "attack_id": "CA-06", "language": "<ISO code: hi | mni | te | ur | pa | ta | or | ml>", "original_claim": "...", "original_evidence": null, "adversarial_claim": "...", "adversarial_evidence": null, "gold_label": "SUP | REF | NEI", "target_label": "SUP | REF | NEI | same_as_gold", "edit_granularity": "sentence", "technique_params": { "attack_name": "Fact Mixing" }, "validity_flags": { "fluency_checked": true, "label_consistent": true, "meaning_preserved": true } }
```

## 6A. Implementation Notes *(input — engineering constraints only, no claims about effectiveness)*
This attack depends heavily on how strong the available generative model is for your specific language — many multilingual LMs vary a lot in fluency across languages. A fluency check (native-speaker review or a language-appropriate perplexity/grammar scorer) is a required validity gate before using generated claims, regardless of which language you're working in.

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
| Claim / Evidence | (Article A: Scheme X gives an annual cash benefit to farmers; Article B: Scheme Y provides crop insurance) | Scheme X provides farmers with crop insurance in addition to the annual cash benefit. |
| Label (gold → target) | gold label | Generic (blended fact is not fully supported by either single source) |
| Language | <your language> | <your language> |

## 9. Failure Modes / Skip Conditions
Skip if the two selected evidence articles share no common entity/theme, since the blend would be too disjointed to read as a single fluent claim.
