# Adversarial Attack Description: Entity Disambiguation (Entity Disamb.)

Target languages for this project: **Hindi (hi), Manipuri (mni), Telugu (te), Urdu (ur), Punjabi (pa), Tamil (ta), Odia (or), Malayalam (ml)**

---

## 1. Metadata

| Field | Value |
|---|---|
| Attack ID | `CA-WORD-02` |
| Attack Name | Entity Disambiguation (Entity Disamb.) |
| Category | `claim_attack` |
| Attack Target | `disrupted_retrieval` |
| Edit Granularity | `word` |
| Strategy Type | `rule_based` / `hybrid` |
| Access Assumption | black-box (no access to retrieval or verification model internals) |
| Source Paper | (Kim and Allan, 2019), Sec. 5.1.2 / Fig. 2 (Claim attack → Manipulate → Disrupted retrieval → Word-level) from Liu et al. (2025) survey |

## 2. Description

The Entity Disambiguation attack introduces ambiguous entity mentions into a claim by replacing a specific entity with a name that has multiple possible referents (e.g., replacing "Paris" with a name that could refer to multiple cities or people). This ambiguity confuses the retrieval module, which may retrieve evidence about the wrong entity, or fail to retrieve any conclusive evidence, leading to a downstream NEI or incorrect verdict.

## 3. Preconditions / Required Inputs

| Input | Status | Description |
|---|---|---|
| `claim_text` | **required** | The original claim to be attacked. |
| `evidence_text` | optional | Gold evidence (if available) to identify the correct entity sense. |
| `gold_label` | optional | Original verdict label. |
| `entity_list` | **required** | List of named entities detected in the claim. |
| `disambiguation_pages` | **required** | Resource mapping entities to their ambiguous alternatives (e.g., Wikipedia disambiguation pages, cross-lingual entity aliases). |
| `ner_tool` | **required** | Named-entity recognizer for the target language. |

## 4. Procedure

1. **Entity Detection**: Run the language-specific NER tool over `claim_text` and extract all named entities.
2. **Find Ambiguous Alternatives**: For each detected entity, query the `disambiguation_pages` resource to find ambiguous namesakes (e.g., "Washington" could refer to the U.S. state, the city, or the person).
3. **Select Target Entity**: Prioritize entities that have at least one ambiguous alternative in the target language. Prefer entities whose alternative sense is well-known enough to appear in the retrieval corpus.
4. **Substitute Ambiguous Entity**: Replace the original entity mention with the ambiguous alternative name.
5. **Validate Fluency**: Check that the substituted claim remains grammatically correct and that the ambiguous entity fits naturally into the syntactic context.
6. **Output**: Produce the adversarial claim with `adversarial_evidence` set to `null`.

## 5. Output Schema (JSON)

```json
{
  "attack_id": "CA-WORD-02",
  "language": "hi",
  "original_claim": "वाशिंगटन अमेरिका की राजधानी है।",
  "original_evidence": null,
  "adversarial_claim": "वाशिंगटन एक महत्वपूर्ण स्थान है।",
  "adversarial_evidence": null,
  "gold_label": "SUP",
  "target_label": "same_as_gold",
  "edit_granularity": "word",
  "technique_params": {
    "original_entity": "वाशिंगटन",
    "ambiguous_replacement": "वाशिंगटन",
    "possible_senses": ["अमेरिकी राज्य", "अमेरिकी राजधानी", "जॉर्ज वाशिंगटन"],
    "disambiguation_source": "wikipedia_disambiguation"
  },
  "validity_flags": {
    "fluency_checked": true,
    "label_consistent": true,
    "meaning_preserved": false
  }
}
```

## 6A. Implementation Notes

| Language | Script | Execution Blockers / Requirements (tooling only) |
|---|---|---|
| Hindi | Devanagari | NER tagger; access to Hindi Wikipedia disambiguation pages or Wikidata aliases; script-aware string matching. |
| Manipuri | Meitei Mayek / Bengali | Disambiguation resources are extremely sparse; may need manual gazetteer of ambiguous names. Bengali-script Wikipedia can serve as partial fallback. |
| Telugu | Telugu | NER tagger; Telugu Wikipedia disambiguation pages if available; otherwise use transliterated English ambiguous names. |
| Urdu | Perso-Arabic (RTL) | NER tagger for Urdu; RTL-safe replacement; Urdu Wikipedia disambiguation pages. |
| Punjabi | Gurmukhi | NER tool; Punjabi Wikipedia disambiguation pages; Gurmukhi-script alias tables. |
| Tamil | Tamil | NER tagger; Tamil Wikipedia disambiguation pages; morphological analyzer to check post-substitution agreement. |
| Odia | Odia | NER availability limited; Odia Wikipedia disambiguation pages may be sparse. Gazetteer-based fallback recommended. |
| Malayalam | Malayalam | NER tagger; Malayalam Wikipedia disambiguation pages; compound-splitting may be needed. |

**Generic mechanical checklist:**
- Grapheme-cluster-aware segmentation: **not needed** (word-level edit).
- RTL-safe tokenization/reassembly: **needed for Urdu** when replacing entities.
- Morphological analyzer / stemmer: **helpful** for all Dravidian and Indo-Aryan languages to ensure the ambiguous noun fits the sentence frame.
- Synonym / paraphrase resource or LM: **not needed** (rule-based disambiguation lookup).
- Script-specific confusables/homoglyph table: **not needed**.

## 6B. Empirical Outcome

*(Left blank — to be filled by the evaluation pipeline.)*

```json
{
  "language": "",
  "attack_executed": true,
  "execution_notes": "",
  "verdict_flipped": null,
  "retrieval_disrupted": null,
  "fluency_score": null,
  "human_detectability": null,
  "attack_success_rate": null,
  "notes": ""
}
```

## 7. Success / Validity Criteria

An Entity Disamb. instance is valid when:
- The substituted entity name is genuinely ambiguous (has ≥2 documented senses in the knowledge base).
- The adversarial claim remains syntactically fluent.
- The original gold label is preserved in principle (the claim is still verifiable, but the retrieval module is expected to fetch wrong evidence).
- Retrieval disruption is evidenced by a drop in evidence recall or by retrieved documents referring to the wrong sense.

## 8. Example

| Field | Original | Adversarial |
|---|---|---|
| Claim | George Washington was the first President of the United States. | Washington was the first President of the United States. |
| Label | SUP → SUP (same) | SUP → NEI/REF (retrieval pulls wrong Washington) |
| Language | English (illustrative) | English (illustrative) |

## 9. Failure Modes / Skip Conditions

- **No ambiguous alternatives found**: If the entity has no disambiguation entry, skip and log "no_ambiguity_found".
- **Alternative not in retrieval corpus**: If the ambiguous sense is too obscure to appear in the evidence corpus, skip (attack would not realistically disrupt retrieval).
- **Grammatical incompatibility**: If the ambiguous replacement requires different case/postposition, skip.
- **NER tool unavailable**: Same fallback as EntityLess (gazetteer or skip).
