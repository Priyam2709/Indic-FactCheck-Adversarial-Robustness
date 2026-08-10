# Adversarial Attack Description Document: Evidence Attacks on Automated Fact-Checking (AFC)
**Revision 2** — extracted single-attack file from Evidence_Attack_Descriptions_v2.md

This document contains one attack description from the **14 Evidence Attacks** targeting Automated Fact-Checking (AFC) systems reviewed in *"Adversarial Attacks Against Automated Fact-Checking: A Survey"* (Liu et al., 2025).

---

<a id="4-ea-impret-01"></a>
# 4. EA-IMPRET-01: Imperceptible Character-Level Retrieval Attack

## 1. Metadata
- **Attack ID**: `EA-IMPRET-01`
- **Attack Name**: Imperceptible Character-Level Retrieval Disruption (`Imperceptible_Ret`)
- **Category**: `evidence_attack`
- **Attack Target**: `disrupted_retrieval`
- **Edit Granularity**: `character`
- **Strategy Type**: `rule_based`
- **Access Assumption**: Black-box retrieval (query-based); white-box retrieval score access improves targeting but is not strictly required
- **Source Paper**: Boucher et al. (2022); Liu et al. (2025), Sec. 5.2.2, Table 4

## 2. Description
This attack targets the evidence retrieval component of an AFC system by injecting imperceptible character-level perturbations (homoglyphs or zero-width joiners) specifically into entity mentions within corpus evidence documents. The subword tokenizer of dense/sparse retrievers fails to map the perturbed entity to query entity embeddings, causing a severe drop in document recall.

## 3. Preconditions / Required Inputs
- `original_evidence` (Required): Corpus document containing entity mentions.
- `entity_list` (Required): List of target named entities in the document.
- `access_to_retriever_scores` (Optional): Retrieval ranking score access, if available, to select the most damaging perturbation.
- `homoglyph_map` (Required): Unicode confusable map.

## 4. Procedure
1. Identify all occurrences of `entity_list` tokens within `original_evidence`.
2. For each entity string, replace 1–2 characters with visually identical homoglyphs or insert a zero-width space (`U+200B`).
3. Re-assemble the perturbed text into the index document.
4. Verify that the inverted index / dense embedding of the perturbed document no longer matches clean claim query entities.
5. Save the perturbed evidence document into the corpus.

## 5. Output Schema (JSON)
```json
{
  "attack_id": "EA-IMPRET-01",
  "language": "te",
  "original_claim": "హైదరాబాద్ తెలంగాణ రాజధాని.",
  "original_evidence": "హైదరాబాద్ భారత దేశంలోని తెలంగాణ రాష్ట్ర రాజధాని.",
  "adversarial_claim": null,
  "adversarial_evidence": "హైదరా​బాద్ భారత దేశంలోని తెలంగాణ రాష్ట్ర రాజధాని.",
  "gold_label": "SUP",
  "target_label": "NEI",
  "edit_granularity": "character",
  "technique_params": {
    "perturbed_entity": "హైదరాబాద్",
    "char_injection": "U+200B"
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
| --- | --- | --- |
| Hindi | Devanagari | Grapheme cluster parser, Devanagari confusable lookup table. |
| Manipuri | Meitei Mayek / Bengali (script varies by corpus) | Grapheme parser & confusable table for whichever script the corpus uses. |
| Telugu | Telugu | Telugu grapheme parser & confusable lookup table. |
| Urdu | Perso-Arabic (RTL) | Urdu joiner-aware character parser & RTL handling. |
| Punjabi | Gurmukhi | Gurmukhi grapheme parser & confusable table. |
| Tamil | Tamil | Tamil grapheme parser & confusable table. |
| Odia | Odia | Odia grapheme parser & confusable table. |
| Malayalam | Malayalam | Malayalam grapheme parser & confusable table. |

### Generic Mechanical Checklist
- Grapheme-cluster-aware segmentation available? Yes (CRITICAL)
- RTL-safe tokenization/reassembly available? Yes (for Urdu)
- Morphological analyzer / stemmer available? No
- Synonym / paraphrase resource or LM available for this language? No
- Script-specific confusables/homoglyph table available? Yes (CRITICAL)

## 6B. Empirical Outcome
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
- **Adversarial Evidence Recall (`RecAdvEvd`)**: Significant reduction in evidence recall score (`RecEvd`).
- **Human Detectability**: Zero visible font distortion.

## 8. Example
| Field | Original | Adversarial |
| --- | --- | --- |
| Claim / Evidence | **Evidence**: Hyderabad is the capital of Telangana state. | **Adversarial Evidence**: Hydеrabad is the capital of Telangana state. *(Latin 'e' replaced by Cyrillic 'е')* |
| Label | SUP → NEI | |
| Language | English (`en`) / Telugu (`te`) | |

## 9. Failure Modes / Skip Conditions
- Skip if the retrieval system performs automated NFKC Unicode normalization before indexing.
- Skip if no named entity can be identified in `original_evidence`.
