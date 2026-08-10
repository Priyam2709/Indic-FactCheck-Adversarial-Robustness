# Adversarial Attack Description: CA-03 — Lexically-informed

## 1. Metadata

| Field | Value |
|---|---|
| Attack ID | CA-03 |
| Attack Name | Lexically-informed |
| Category | claim_attack |
| Attack Target | corrupted_verdict |
| Edit Granularity | sentence |
| Strategy Type | hybrid |
| Access Assumption | Black-box |
| Source Paper | Thorne et al., 2019a, Sec. 5.1.1 |

## 2. Description
This attack paraphrases a claim by first swapping out nouns and adjectives for related words (synonyms/related terms), then running the result through a back-translation-style paraphrasing model to smooth it into fluent, natural language. The goal is a claim that reads naturally but has drifted just enough in wording to trip up the verifier.

## 3. Preconditions / Required Inputs
Original claim text (required); a synonym/thesaurus resource for your language, e.g. a WordNet variant if one exists (required); a paraphrasing or back-translation model that supports your language (required for the fluency pass).

## 4. Procedure
1. Identify nouns and adjectives in the claim using a POS tagger for your language.
2. Replace each with a close synonym from a lexical resource in your language.
3. Pass the substituted sentence through a paraphrasing/back-translation model to restore natural fluency.
4. Manually or automatically confirm the paraphrase preserves the original meaning and gold label.

## 5. Output Schema (JSON)
```json
{ "attack_id": "CA-03", "language": "<ISO code: hi | mni | te | ur | pa | ta | or | ml>", "original_claim": "...", "original_evidence": null, "adversarial_claim": "...", "adversarial_evidence": null, "gold_label": "SUP | REF | NEI", "target_label": "SUP | REF | NEI | same_as_gold", "edit_granularity": "sentence", "technique_params": { "attack_name": "Lexically-informed" }, "validity_flags": { "fluency_checked": true, "label_consistent": true, "meaning_preserved": true } }
```

## 6A. Implementation Notes *(input — engineering constraints only, no claims about effectiveness)*
This is one of the harder attacks to port for lower-resource languages: check whether a maintained WordNet-style resource exists for your language before starting (coverage varies a lot — e.g., IndoWordNet covers several Indian languages but unevenly). Where coverage is thin, an LLM-based synonym suggestion in your target language is a reasonable fallback — just verify register/formality is preserved.

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
| Claim / Evidence | The government launched a new housing scheme for poor families. | The administration initiated a new residential scheme for underprivileged families. |
| Label (gold → target) | gold label | SUP → NEI (retrieval may fail to match rarer synonyms to evidence wording) |
| Language | <your language> | <your language> |

## 9. Failure Modes / Skip Conditions
Skip if key nouns/adjectives have no usable synonym entry in the available lexical resource for your language.
