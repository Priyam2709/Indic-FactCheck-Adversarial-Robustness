# Adversarial Attack Description: Character Insertion

## 1. Metadata

| Field | Value |
|---|---|
| Attack ID | `CA_CHAR_03_CharacterInsertion` |
| Attack Name | Character Insertion |
| Category | `claim_attack` |
| Attack Target | `corrupted_verdict` |
| Edit Granularity | `character` |
| Strategy Type | `rule_based` |
| Access Assumption | black-box (verification + retrieval) |
| Source Paper | (Mamta & Cocarascu, 2025) — FactEval benchmark; catalogued in (Liu et al., 2025) Sec. 5.1.2 |

## 2. Description
This attack selects a non-initial, non-final character within a word and inserts a copy of it immediately after the selected position. The inserted grapheme creates local orthographic noise that can misalign tokenization and embeddings, leading to incorrect verdict predictions while the claim remains superficially readable.

## 3. Preconditions / Required Inputs

| Input | Status | Description |
|---|---|---|
| `claim_text` | **required** | The original claim string to be perturbed. |
| `gold_label` | **required** | Original verdict label (`SUP`, `REF`, or `NEI`). |
| `language` | **required** | ISO 639-1/3 code (must be one of: `hi`, `mni`, `te`, `ur`, `pa`, `ta`, `or`, `ml`). |
| `insertion_budget` | optional | Maximum insertions per claim (default: 1). |
| `grapheme_cluster_tool` | optional | Library/tool for Unicode extended grapheme cluster segmentation (strongly recommended). |

## 4. Procedure

1. **Language Detection** — Confirm `language` is in the supported set. If not, skip and log.
2. **Tokenization** — Segment the claim into words (whitespace-delimited tokens).
3. **Candidate Selection** — For each word of length ≥ 3 grapheme clusters, identify all non-initial and non-final characters.
4. **Grapheme-Aware Insertion** — Select one candidate uniformly at random and insert a copy of the same grapheme immediately after it. Reassemble the word.
   - For abugidas, ensure the insertion does not split a conjunct consonant or virama sequence. If the resulting cluster is invalid, discard and resample.
   - For Urdu, ensure insertion preserves cursive joining contexts.
5. **Reassembly** — Replace the original word in the claim string. Preserve whitespace, punctuation, and casing.
6. **Validity Check** — Verify at least one insertion was successfully applied. If none succeeded, skip.
7. **Output Packaging** — Populate the JSON output schema.

## 5. Output Schema (JSON)

```json
{
  "attack_id": "CA_CHAR_03_CharacterInsertion",
  "language": "te",
  "original_claim": "హైదరాబాద్ తెలంగాణ రాజధాని.",
  "original_evidence": null,
  "adversarial_claim": "హైదరాబాద్ తెలంగాణ రాజధాని.",
  "adversarial_evidence": null,
  "gold_label": "SUP",
  "target_label": "same_as_gold",
  "edit_granularity": "character",
  "technique_params": {
    "insertion_type": "self_character",
    "insertions_applied": 1,
    "affected_word": "రాజధాని",
    "grapheme_aware": true
  },
  "validity_flags": {
    "fluency_checked": false,
    "label_consistent": true,
    "meaning_preserved": false
  }
}
```

## 6A. Implementation Notes *(engineering constraints only)*

| Language | Script | Execution Blockers / Requirements (tooling only) |
|---|---|---|
| Hindi | Devanagari | **Grapheme-cluster-aware segmentation required.** Inserting inside a conjunct can break it. Skip if no segmenter. |
| Manipuri | Meitei Mayek / Bengali | **Grapheme clustering required.** Skip if unavailable. |
| Telugu | Telugu | **Grapheme clustering required.** Subscript conjuncts must stay intact. Skip if unavailable. |
| Urdu | Perso-Arabic (RTL) | **RTL-safe tokenization + grapheme clustering required.** Skip if no shaping library. |
| Punjabi | Gurmukhi | **Grapheme clustering required.** Skip if unavailable. |
| Tamil | Tamil | **Grapheme clustering strongly recommended.** Skip if no segmenter. |
| Odia | Odia | **Grapheme clustering required.** Skip if unavailable. |
| Malayalam | Malayalam | **Grapheme clustering required.** Skip if unavailable. |

### Generic Mechanical Checklist
- **Grapheme-cluster-aware segmentation available?** **REQUIRED** for all languages. If missing → skip or fallback to `CA_WORD_04` (Typos).
- **RTL-safe tokenization/reassembly available?** **REQUIRED** for Urdu only.
- **Morphological analyzer / stemmer?** Not required.
- **Synonym / paraphrase resource or LM?** Not required.
- **Script-specific confusables/homoglyph table?** Not required.

## 6B. Empirical Outcome *(output — left blank; filled by evaluation pipeline)*

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

1. **Structural validity** — The adversarial claim differs by one or more internal character insertions.
2. **Orthographic validity** — All insertions produce valid Unicode strings.
3. **Fluency preservation** — The claim remains pronounceable/typable.
4. **Label consistency (input side)** — Gold label preserved; no presupposed target verdict.
5. **Evaluation metrics** — Potency, Correctness Rate, Resilience.

## 8. Example

| Field | Original | Adversarial |
|---|---|---|
| Claim | హైదరాబాద్ తెలంగాణ రాజధాని. | హైదరాబాద్ తెలంగాణ రాజధాని. |
| Label | SUP → (any flip) | Gold retained as SUP; target is generic flip |
| Language | Telugu (te) | Telugu (te) |
| Edit detail | — | Insertion of `ధ` after itself in `రాజధాని` → `రాజధ్ధాని` |

## 9. Failure Modes / Skip Conditions

1. **Claim too short** — No word with ≥ 3 grapheme clusters.
2. **Missing grapheme cluster support** — Skip and log reason.
3. **Invalid orthography after insertion** — If insertion breaks a conjunct/RTL join, discard. If all candidates fail, skip.
4. **Language not in target set** — Skip immediately.
