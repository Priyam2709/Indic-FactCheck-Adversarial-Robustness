# Adversarial Attack Description: EntityLinking

Target languages for this project: **Hindi (hi), Manipuri (mni), Telugu (te), Urdu (ur), Punjabi (pa), Tamil (ta), Odia (or), Malayalam (ml)**

---

## 1. Metadata

| Field | Value |
|---|---|
| Attack ID | `CA-WORD-03` |
| Attack Name | EntityLinking |
| Category | `claim_attack` |
| Attack Target | `disrupted_retrieval` |
| Edit Granularity | `word` |
| Strategy Type | `rule_based` / `hybrid` |
| Access Assumption | black-box (no access to retrieval or verification model internals) |
| Source Paper | (Kim and Allan, 2019), Sec. 5.1.2 / Fig. 2 (Claim attack → Manipulate → Disrupted retrieval → Word-level) from Liu et al. (2025) survey |

## 2. Description

The EntityLinking attack substitutes a named entity in the claim with an uncommon or rarely-used alias, nickname, or transliteration variant that is valid but unlikely to be indexed by the retrieval system. By using a non-standard entity mention, the retrieval module fails to match the claim against the canonical evidence sentences, disrupting evidence recall and causing downstream verdict errors.

## 3. Preconditions / Required Inputs

| Input | Status | Description |
|---|---|---|
| `claim_text` | **required** | The original claim to be attacked. |
| `evidence_text` | optional | Gold evidence (if available) to verify that the alias is valid but uncommon. |
| `gold_label` | optional | Original verdict label. |
| `entity_list` | **required** | List of named entities detected in the claim. |
| `entity_alias_table` | **required** | Mapping from canonical entity names to uncommon aliases, nicknames, or variant spellings in the target language. |
| `ner_tool` | **required** | Named-entity recognizer for the target language. |

## 4. Procedure

1. **Entity Detection**: Run the language-specific NER tool over `claim_text` and extract all named entities.
2. **Alias Lookup**: For each entity, query the `entity_alias_table` for uncommon aliases. An "uncommon" alias is defined as one that appears in the knowledge base but with significantly lower frequency than the canonical name.
3. **Select Target Entity**: Choose the entity that has the most uncommon alias available. If multiple aliases exist, select the one with the lowest corpus frequency or the one least likely to be indexed by the retriever.
4. **Substitute Alias**: Replace the canonical entity mention with the selected uncommon alias.
5. **Validate Fluency**: Ensure the alias fits grammatically into the claim (e.g., correct honorifics, postpositions, case endings).
6. **Output**: Produce the adversarial claim with `adversarial_evidence` set to `null`.

## 5. Output Schema (JSON)

```json
{
  "attack_id": "CA-WORD-03",
  "language": "hi",
  "original_claim": "महात्मा गांधी भारत के राष्ट्रपिता थे।",
  "original_evidence": null,
  "adversarial_claim": "मोहनदास करमचंद गांधी भारत के राष्ट्रपिता थे।",
  "adversarial_evidence": null,
  "gold_label": "SUP",
  "target_label": "same_as_gold",
  "edit_granularity": "word",
  "technique_params": {
    "canonical_entity": "महात्मा गांधी",
    "uncommon_alias": "मोहनदास करमचंद गांधी",
    "alias_frequency_rank": 47,
    "alias_source": "wikidata_aliases"
  },
  "validity_flags": {
    "fluency_checked": true,
    "label_consistent": true,
    "meaning_preserved": true
  }
}
```

## 6A. Implementation Notes

| Language | Script | Execution Blockers / Requirements (tooling only) |
|---|---|---|
| Hindi | Devanagari | NER tagger; Wikidata alias dump filtered for Hindi; frequency statistics from Hindi Wikipedia dump to rank alias uncommonness. |
| Manipuri | Meitei Mayek / Bengali | Alias resources are extremely limited. May need to transliterate from English aliases or use Bengali-script Wikidata aliases as fallback. |
| Telugu | Telugu | NER tagger; Telugu Wikidata aliases; frequency ranking from Telugu Wikipedia. |
| Urdu | Perso-Arabic (RTL) | NER tagger; Urdu Wikidata aliases; RTL-safe replacement; frequency ranking from Urdu Wikipedia. |
| Punjabi | Gurmukhi | NER tool; Gurmukhi Wikidata aliases; frequency ranking from Punjabi Wikipedia. |
| Tamil | Tamil | NER tagger; Tamil Wikidata aliases; morphological analyzer to adjust case/postposition after alias substitution. |
| Odia | Odia | NER limited; Odia Wikidata aliases may be sparse. Gazetteer of formal vs. informal names recommended as fallback. |
| Malayalam | Malayalam | NER tagger; Malayalam Wikidata aliases; compound splitting may be needed for long proper names. |

**Generic mechanical checklist:**
- Grapheme-cluster-aware segmentation: **not needed** (word-level edit).
- RTL-safe tokenization/reassembly: **needed for Urdu** when replacing multi-word entities.
- Morphological analyzer / stemmer: **helpful** for adjusting postpositions/case after alias substitution in agglutinative languages (Tamil, Telugu, Malayalam).
- Synonym / paraphrase resource or LM: **not needed** (alias lookup).
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

An EntityLinking instance is valid when:
- The substituted alias is a genuine, documented alternative name for the entity.
- The alias is demonstrably less common than the canonical name in the target language corpus.
- The adversarial claim remains syntactically fluent.
- The original gold label is preserved (the claim is still factually verifiable).
- Retrieval disruption is evidenced by a drop in evidence recall@k or by the retriever failing to surface the canonical evidence.

## 8. Example

| Field | Original | Adversarial |
|---|---|---|
| Claim | The Eiffel Tower is located in Paris. | The Iron Lady is located in Paris. |
| Label | SUP → SUP (same) | SUP → NEI (retriever misses "Iron Lady") |
| Language | English (illustrative) | English (illustrative) |

## 9. Failure Modes / Skip Conditions

- **No uncommon alias found**: If the entity has no aliases or only one very common alias, skip and log "no_uncommon_alias".
- **Alias not in retrieval vocabulary**: If the alias is so rare that it is OOV for the retriever, the attack may trivially fail; still execute but log "alias_oov".
- **Grammatical incompatibility**: If the alias requires different morphological marking, skip or apply morphological adjustment if tooling permits.
- **NER tool unavailable**: Same fallback as EntityLess.
