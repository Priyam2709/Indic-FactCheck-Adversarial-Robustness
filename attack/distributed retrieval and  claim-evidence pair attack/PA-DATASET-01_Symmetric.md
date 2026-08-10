# Adversarial Attack Description: Symmetric

Target languages for this project: **Hindi (hi), Manipuri (mni), Telugu (te), Urdu (ur), Punjabi (pa), Tamil (ta), Odia (or), Malayalam (ml)**

---

## 1. Metadata

| Field | Value |
|---|---|
| Attack ID | `PA-DATASET-01` |
| Attack Name | Symmetric |
| Category | `pair_attack` |
| Attack Target | `corrupted_verdict` |
| Edit Granularity | `dataset` |
| Strategy Type | `rule_based` |
| Access Assumption | black-box (no access to FC verification or retrieval models) |
| Source Paper | (Schuster et al., 2019), Sec. 5.3.1 / Fig. 2 (Claim-evidence pair attack → Generate → Corrupted verdict → Dataset-level) from Liu et al. (2025) survey |

## 2. Description

The Symmetric attack manually constructs synthetic claim-evidence pairs that retain the original relational label (SUPPORTS or REFUTES) while introducing contradictory factual content. Starting from an existing FEVER-style claim-evidence pair, the attacker permutes the claim and evidence to create cross-pairs with inverse labels, forming an unbiased evaluation dataset (FEVER-sym) that exposes spurious correlations learned by FC models.

## 3. Preconditions / Required Inputs

| Input | Status | Description |
|---|---|---|
| `original_claim` | **required** | The original claim from the seed dataset. |
| `original_evidence` | **required** | The original evidence sentence(s) paired with the claim. |
| `gold_label` | **required** | Original label of the pair (SUP or REF). |
| `claim_evidence_pool` | **required** | A pool of existing claim-evidence pairs to draw from for permutation. |
| `human_annotators` | **required** | For manual validation of generated pairs (Schuster et al. used native speakers). |

## 4. Procedure

1. **Select Seed Pair**: Choose an original claim-evidence pair with label SUP or REF from the `claim_evidence_pool`.
2. **Generate Cross-Pair (Inverse Label)**: 
   - If original is SUP (claim C + evidence E supporting C), create a new pair by combining claim C with a modified evidence E' that contradicts C, yielding REF.
   - If original is REF (claim C + evidence E refuting C), create a new pair by combining claim C with a modified evidence E' that supports C, yielding SUP.
3. **Preserve Surface Form**: Ensure the new pair maintains similar lexical overlap and syntactic structure to the original, so that models cannot rely on simple n-gram correlation heuristics.
4. **Manual Validation**: Have annotators verify that the new pair is correctly labeled and grammatically valid.
5. **Dataset Assembly**: Collect all original and generated pairs to form the symmetric dataset. Each original pair spawns two additional cross-pairs with inverse labels.
6. **Output**: Produce the adversarial claim-evidence pair with both fields populated.

## 5. Output Schema (JSON)

```json
{
  "attack_id": "PA-DATASET-01",
  "language": "hi",
  "original_claim": "नई दिल्ली भारत की राजधानी है।",
  "original_evidence": "भारत की राजधानी नई दिल्ली है।",
  "adversarial_claim": "नई दिल्ली भारत की राजधानी है।",
  "adversarial_evidence": "मुंबई भारत की वित्तीय राजधानी है; नई दिल्ली केवल प्रशासनिक केंद्र है।",
  "gold_label": "SUP",
  "target_label": "REF",
  "edit_granularity": "dataset",
  "technique_params": {
    "generation_method": "manual_cross_pair",
    "seed_pair_id": "fever-12345",
    "label_inversion": true,
    "human_validated": true
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
| Hindi | Devanagari | Existing Hindi FC dataset (or translated FEVER pairs); human annotators fluent in Hindi; claim-evidence alignment checking tool. |
| Manipuri | Meitei Mayek / Bengali | Extremely limited FC datasets; may need to construct from scratch using Bengali-script Wikipedia. Human annotators are critical. |
| Telugu | Telugu | Telugu FC dataset or translated pairs; human annotators; script-aware evidence editing tools. |
| Urdu | Perso-Arabic (RTL) | Urdu FC dataset or translated pairs; RTL-aware annotation interface; human annotators. |
| Punjabi | Gurmukhi | Punjabi FC dataset or translated pairs; human annotators; Gurmukhi-script editing support. |
| Tamil | Tamil | Tamil FC dataset or translated pairs; human annotators; morphological tools for evidence rewriting. |
| Odia | Odia | Odia FC dataset or translated pairs; human annotators; limited digital resources. |
| Malayalam | Malayalam | Malayalam FC dataset or translated pairs; human annotators; compound-word handling for evidence generation. |

**Generic mechanical checklist:**
- Grapheme-cluster-aware segmentation: **not needed** (dataset-level generation).
- RTL-safe tokenization/reassembly: **needed for Urdu** during evidence rewriting.
- Morphological analyzer / stemmer: **helpful** for evidence rewriting in all target languages.
- Synonym / paraphrase resource or LM: **helpful** for generating contradictory evidence that preserves surface similarity.
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

A Symmetric instance is valid when:
- The adversarial pair has the inverse label of the original pair (SUP ↔ REF).
- The claim text is reused from the original pool (ensuring lexical overlap is preserved).
- The evidence is manually verified to correctly support or refute the claim.
- The pair is grammatically fluent and semantically coherent in the target language.
- The dataset as a whole exposes model bias (measured by accuracy drop on symmetric pairs vs. original pairs).

## 8. Example

| Field | Original | Adversarial |
|---|---|---|
| Claim | The Eiffel Tower is in Paris. | The Eiffel Tower is in Paris. |
| Evidence | The Eiffel Tower is located in Paris, France. | The Eiffel Tower is located in Berlin, Germany. |
| Label | SUP → REF | SUP → REF |
| Language | English (illustrative) | English (illustrative) |

## 9. Failure Modes / Skip Conditions

- **No suitable contradictory evidence**: If the claim is too specific to easily generate a plausible contradictory evidence sentence, skip and log "no_contradictory_evidence".
- **Human annotation unavailable**: If no fluent annotator is available for the target language, skip (this attack requires human validation).
- **Dataset too small**: If the seed pool has fewer than 100 pairs, the symmetric extension may not yield statistically meaningful results; log "insufficient_seed_data".
- **Label ambiguity**: If annotators disagree on the label (Cohen κ < 0.7), discard the pair.
