# Adversarial Attack Description: EntityLess

Target languages for this project: **Hindi (hi), Manipuri (mni), Telugu (te), Urdu (ur), Punjabi (pa), Tamil (ta), Odia (or), Malayalam (ml)**

---

## 1. Metadata

| Field | Value |
|---|---|
| Attack ID | `CA-WORD-01` |
| Attack Name | EntityLess |
| Category | `claim_attack` |
| Attack Target | `disrupted_retrieval` |
| Edit Granularity | `word` |
| Strategy Type | `rule_based` |
| Access Assumption | black-box (no access to retrieval or verification model internals) |
| Source Paper | (Kim and Allan, 2019), Sec. 5.1.2 / Fig. 2 (Claim attack → Manipulate → Disrupted retrieval → Word-level) from Liu et al. (2025) survey |

## 2. Description

The EntityLess attack replaces specific named entities in a claim with generic hypernyms or type-level terms (e.g., "Harvard University" → "university"). By stripping away discriminative entity mentions, the attack prevents the retrieval module from locating the precise evidence documents or sentences needed to verify the claim, thereby causing the AFC system to return incorrect or incomplete verdicts due to missing or irrelevant evidence.

## 3. Preconditions / Required Inputs

| Input | Status | Description |
|---|---|---|
| `claim_text` | **required** | The original claim to be attacked. |
| `evidence_text` | optional | Gold evidence (if available) to verify that the generic replacement still leaves the claim semantically checkable. |
| `gold_label` | optional | Original verdict label (SUP / REF / NEI). |
| `entity_list` | **required** | List of named entities detected in the claim. |
| `entity_type_map` | **required** | Mapping from each entity to its generic hypernym or type (e.g., PER → "person", ORG → "organization", GPE → "country"). |
| `ner_tool` | **required** | Named-entity recognizer for the target language. |

## 4. Procedure

1. **Entity Detection**: Run the language-specific NER tool over `claim_text` and extract all named entities with their types.
2. **Filter Candidates**: Retain only entities whose types have a known generic replacement in the `entity_type_map`. Skip entities that are already generic or whose type is unknown.
3. **Select Target Entity**: Choose one or more entities to replace. Priority order: (a) entities that appear in the gold evidence (if known), (b) the most salient entity (first proper noun), (c) random selection.
4. **Generate Generic Replacement**: Substitute each selected entity with its generic hypernym from the `entity_type_map`.
5. **Validate Fluency**: Ensure the resulting claim is grammatically coherent in the target language (e.g., correct case marking, postpositions, verb agreement). If grammatical collapse occurs, try the next entity in the candidate list.
6. **Output**: Produce the adversarial claim with `adversarial_evidence` set to `null`.

## 5. Output Schema (JSON)

```json
{
  "attack_id": "CA-WORD-01",
  "language": "hi",
  "original_claim": "हार्वर्ड विश्वविद्यालय 1636 में स्थापित किया गया था।",
  "original_evidence": null,
  "adversarial_claim": "विश्वविद्यालय 1636 में स्थापित किया गया था।",
  "adversarial_evidence": null,
  "gold_label": "SUP",
  "target_label": "same_as_gold",
  "edit_granularity": "word",
  "technique_params": {
    "replaced_entities": ["हार्वर्ड विश्वविद्यालय"],
    "replacements": ["विश्वविद्यालय"],
    "entity_types": ["ORG"]
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
| Hindi | Devanagari | NER tagger with support for PER, ORG, GPE tags; hypernym lexicon or WordNet-style type mapping for Devanagari nouns. |
| Manipuri | Meitei Mayek / Bengali | NER availability is limited; may need fallback to dictionary-based proper-noun detection. Script-specific tokenization required if using Bengali script. |
| Telugu | Telugu | NER tagger (e.g., AI4Bharat or in-house); generic replacement must handle Telugu compounding and agglutination. |
| Urdu | Perso-Arabic (RTL) | NER tagger for Urdu; RTL-safe string replacement to avoid breaking character order during substitution. |
| Punjabi | Gurmukhi | NER tool for Gurmukhi script; hypernym resources are sparse—may require manual type table. |
| Tamil | Tamil | NER tagger with entity type labels; morphological analyzer helpful for post-replacement agreement checking. |
| Odia | Odia | NER availability is limited; may need rule-based proper noun detection using capitalization heuristics (Odia has no case distinction, so rely on gazetteers). |
| Malayalam | Malayalam | NER tagger; compound word splitting may be needed before generic substitution. |

**Generic mechanical checklist:**
- Grapheme-cluster-aware segmentation: **not needed** (word-level edit).
- RTL-safe tokenization/reassembly: **needed for Urdu** when replacing multi-word entities.
- Morphological analyzer / stemmer: **helpful** for all languages to verify post-substitution agreement.
- Synonym / paraphrase resource or LM: **not needed** (rule-based hypernym lookup).
- Script-specific confusables/homoglyph table: **not needed**.

## 6B. Empirical Outcome

*(Left blank — to be filled by the evaluation pipeline after running the attack against a real FC model in the target language.)*

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

An EntityLess instance is considered valid for evaluation when:
- The adversarial claim remains grammatically fluent and semantically meaningful in the target language.
- At least one named entity has been successfully replaced by a generic term.
- The replacement does not alter the original gold label (i.e., the claim is still theoretically verifiable if the correct evidence were retrieved).
- Retrieval disruption is measured by a drop in recall@k or evidence overlap compared to the original claim.

## 8. Example

| Field | Original | Adversarial |
|---|---|---|
| Claim | Harvard University was founded in 1636. | A university was founded in 1636. |
| Label | SUP → SUP (same) | SUP → NEI (retrieval fails) |
| Language | English (illustrative) | English (illustrative) |

*Note: Actual deployment uses the 8 target languages.*

## 9. Failure Modes / Skip Conditions

- **No entities detected**: If the NER tool returns zero entities, skip and log "no_entities_found" in `execution_notes`.
- **No type mapping available**: If an entity's type is not in the `entity_type_map`, skip that entity. If all entities lack mappings, skip the instance.
- **Grammatical collapse**: If replacement destroys fluency (e.g., case/agreement mismatch), skip and try the next candidate entity.
- **NER tool unavailable for language**: If no NER model exists for the target language, fall back to dictionary-based gazetteer matching or skip and log "ner_unavailable".
