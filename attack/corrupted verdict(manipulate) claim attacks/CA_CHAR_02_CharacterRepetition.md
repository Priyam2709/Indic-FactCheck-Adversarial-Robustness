# Adversarial Attack Description: Character Repetition

## 1. Metadata

| Field | Value |
|---|---|
| Attack ID | `CA_CHAR_02_CharacterRepetition` |
| Attack Name | Character Repetition |
| Category | `claim_attack` |
| Attack Target | `corrupted_verdict` |
| Edit Granularity | `character` |
| Strategy Type | `rule_based` |
| Access Assumption | black-box (verification + retrieval) |
| Source Paper | (Mamta & Cocarascu, 2025) — FactEval benchmark; catalogued in (Liu et al., 2025) Sec. 5.1.2 |

## 2. Description
This attack duplicates a randomly selected non-initial, non-final character within a word in the claim. The resulting orthographic redundancy corrupts token boundaries and subword segmentation, potentially causing the fact-checking model to misclassify the claim while the text remains superficially readable.

## 3. Preconditions / Required Inputs

| Input | Status | Description |
|---|---|---|
| `claim_text` | **required** | The original claim string to be perturbed. |
| `gold_label` | **required** | Original verdict label (`SUP`, `REF`, or `NEI`). |
| `language` | **required** | ISO 639-1/3 code (must be one of: `hi`, `mni`, `te`, `ur`, `pa`, `ta`, `or`, `ml`). |
| `repetition_budget` | optional | Maximum number of characters to duplicate (default: 1 per claim). |
| `grapheme_cluster_tool` | optional | Library/tool for Unicode extended grapheme cluster segmentation (strongly recommended). |

## 4. Procedure

1. **Language Detection** — Confirm `language` is in the supported set. If not, skip and log.
2. **Tokenization** — Segment the claim into words (whitespace-delimited tokens).
3. **Candidate Selection** — For each word of length ≥ 3 grapheme clusters, identify all non-initial and non-final characters (grapheme clusters) that can be duplicated without producing a visually identical result.
4. **Grapheme-Aware Duplication** — Using grapheme-cluster-aware segmentation, select one candidate uniformly at random and duplicate it immediately after itself. Reassemble the word.
   - For abugidas (Devanagari, Telugu, Gurmukhi, Tamil, Odia, Malayalam, Bengali/Meitei Mayek), ensure the duplication does not split a conjunct consonant or virama sequence. If duplication produces an invalid orthographic cluster, discard and resample.
   - For Urdu (RTL Perso-Arabic), ensure duplication respects cursive joining contexts. Do not duplicate a joining character in a way that breaks word shaping.
5. **Reassembly** — Replace the original word with the duplicated version in the claim string. Preserve original whitespace, punctuation, and casing.
6. **Validity Check** — Verify the adversarial claim is non-empty and that at least one duplication was successfully applied. If zero duplications succeeded, skip the instance.
7. **Output Packaging** — Populate the JSON output schema and flag for downstream checks.

## 5. Output Schema (JSON)

```json
{
  "attack_id": "CA_CHAR_02_CharacterRepetition",
  "language": "hi",
  "original_claim": "भारत की राजधानी दिल्ली है।",
  "original_evidence": null,
  "adversarial_claim": "भार्रत की राजधानी दिल्ली है।",
  "adversarial_evidence": null,
  "gold_label": "SUP",
  "target_label": "same_as_gold",
  "edit_granularity": "character",
  "technique_params": {
    "duplication_type": "internal_character",
    "duplications_applied": 1,
    "affected_word": "भारत",
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
| Hindi | Devanagari | **Grapheme-cluster-aware segmentation required.** Duplicating a character inside a conjunct (e.g., क्ष → क्ष्ष) may produce invalid orthography. If no segmenter available, skip or fallback to `CA_WORD_04` (Typos). |
| Manipuri | Meitei Mayek / Bengali | **Grapheme clustering required.** Bengali conjuncts and Meitei Mayek clusters must not be split. Skip if no segmenter. |
| Telugu | Telugu | **Grapheme clustering required.** Subscripted conjuncts must remain intact. Skip if unavailable. |
| Urdu | Perso-Arabic (RTL) | **RTL-safe tokenization + grapheme clustering required.** Duplication must preserve joining logic. Skip if no Arabic-script shaping library available. |
| Punjabi | Gurmukhi | **Grapheme clustering required.** Addak, tippi, and conjuncts must not be split. Skip if unavailable. |
| Tamil | Tamil | **Grapheme clustering strongly recommended.** Pulli (dot) must stay attached to its consonant. Skip if no segmenter. |
| Odia | Odia | **Grapheme clustering required.** Conjunct consonants must not be split. Skip if unavailable. |
| Malayalam | Malayalam | **Grapheme clustering required.** Chillu characters and stacked conjuncts are atomic; must not be split. Skip if unavailable. |

### Generic Mechanical Checklist
- **Grapheme-cluster-aware segmentation available?** **REQUIRED** for all languages. If missing → skip or fallback to `CA_WORD_04` (Typos).
- **RTL-safe tokenization/reassembly available?** **REQUIRED** for Urdu only. If missing → skip Urdu instances.
- **Morphological analyzer / stemmer?** Not required.
- **Synonym / paraphrase resource or LM?** Not required.
- **Script-specific confusables/homoglyph table?** Not required (needed for `CA_CHAR_05`).

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

1. **Structural validity** — The adversarial claim differs from the original by exactly one or more internal character duplications; no words added or deleted.
2. **Orthographic validity** — All duplications produce valid Unicode strings in the target script.
3. **Fluency preservation** — The claim remains pronounceable/typable (low human detectability).
4. **Label consistency (input side)** — Gold label preserved in metadata; attack does not presuppose a target verdict.
5. **Evaluation metrics** — Potency, Correctness Rate, Resilience (see Appendix C.2 of survey).

## 8. Example

| Field | Original | Adversarial |
|---|---|---|
| Claim | भारत की राजधानी दिल्ली है। | भार्रत की राजधानी दिल्ली है। |
| Label | SUP → (any flip) | Gold retained as SUP; target is generic flip |
| Language | Hindi (hi) | Hindi (hi) |
| Edit detail | — | Duplication of `र` in `भारत` → `भार्रत` |

## 9. Failure Modes / Skip Conditions

1. **Claim too short** — No word with ≥ 3 grapheme clusters.
2. **All candidates are no-ops** — Duplicating would produce identical string.
3. **Missing grapheme cluster support** — Skip and log: "Missing grapheme cluster segmenter for {language}."
4. **Invalid orthography after duplication** — If duplication breaks a conjunct/RTL join, discard candidate. If all fail, skip.
5. **Language not in target set** — Skip immediately.
