# Adversarial Attack Description: Phonetic Perturbation

## 1. Metadata

| Field | Value |
|---|---|
| Attack ID | `CA_WORD_13_PhoneticPerturbation` |
| Attack Name | Phonetic Perturbation |
| Category | `claim_attack` |
| Attack Target | `corrupted_verdict` |
| Edit Granularity | `word` |
| Strategy Type | `rule_based` |
| Access Assumption | black-box (verification + retrieval) |
| Source Paper | (Mamta & Cocarascu, 2025) — FactEval benchmark; catalogued in (Liu et al., 2025) Sec. 5.1.2 |

## 2. Description
This attack applies phonetic perturbations using a human-written dictionary with a word-level perturbation budget. It replaces words with phonetically similar alternatives that are spelled differently, exploiting the gap between phonetic and orthographic representations in fact-checking models.

## 3. Preconditions / Required Inputs

| Input | Status | Description |
|---|---|---|
| `claim_text` | **required** | The original claim string to be perturbed. |
| `gold_label` | **required** | Original verdict label (SUP, REF, or NEI). |
| `language` | **required** | ISO 639-1/3 code (must be one of: hi, mni, te, ur, pa, ta, or, ml). |
| `phonetic_dictionary` | **required** | A mapping from words to their phonetically similar spelling variants for the target language. |
| `perturbation_budget` | optional | Maximum number of words to perturb (default: 1). |

## 4. Procedure

1. **Language Detection** — Confirm `language` is in the supported set. If not, skip and log.
2. **Load Phonetic Dictionary** — Load the phonetic mapping for the target language. If no dictionary exists, skip and log.
3. **Candidate Scan** — Scan the claim for words that appear as keys in the phonetic dictionary.
   - If no candidates are found, skip the instance.
4. **Substitution** — Select up to `perturbation_budget` candidates uniformly at random and replace each with one of its phonetic variants (randomly chosen if multiple exist).
5. **Reassembly** — Reconstruct the claim string. Preserve surrounding whitespace and punctuation.
6. **Validity Check** — Verify the claim text has changed. If no substitution was applied, skip.
7. **Output Packaging** — Populate the JSON output schema.

## 5. Output Schema (JSON)

```json
{
  "attack_id": "CA_WORD_13_PhoneticPerturbation",
  "language": "pa",
  "original_claim": "ਅੰਮ੍ਰਿਤਸਰ ਪੰਜਾਬ ਦਾ ਸ਼ਹਿਰ ਹੈ।",
  "original_evidence": null,
  "adversarial_claim": "ਅੰਮ੍ਰਿਤਸਰ ਪੰਜਾਬ ਦਾ ਸਹਿਰ ਹੈ।",
  "adversarial_evidence": null,
  "gold_label": "SUP",
  "target_label": "same_as_gold",
  "edit_granularity": "word",
  "technique_params": {
    "substitution_type": "phonetic_variant",
    "original_word": "ਸ਼ਹਿਰ",
    "phonetic_variant": "ਸਹਿਰ",
    "perturbations_applied": 1
  },
  "validity_flags": {
    "fluency_checked": false,
    "label_consistent": true,
    "meaning_preserved": false
  }
}
```

## 6A. Implementation Notes

| Language | Script | Execution Blockers / Requirements (tooling only) |
|---|---|---|
| Hindi | Devanagari | **Phonetic dictionary required.** Must map Hindi words to phonetically similar but orthographically distinct variants. If unavailable, skip. |
| Manipuri | Meitei Mayek / Bengali | **Phonetic dictionary required.** If no dictionary, skip. |
| Telugu | Telugu | **Phonetic dictionary required.** If no dictionary, skip. |
| Urdu | Perso-Arabic (RTL) | **Phonetic dictionary required.** If no dictionary, skip. |
| Punjabi | Gurmukhi | **Phonetic dictionary required.** If no dictionary, skip. |
| Tamil | Tamil | **Phonetic dictionary required.** If no dictionary, skip. |
| Odia | Odia | **Phonetic dictionary required.** If no dictionary, skip. |
| Malayalam | Malayalam | **Phonetic dictionary required.** If no dictionary, skip. |

### Generic Mechanical Checklist
- **Phonetic dictionary for the language?** **REQUIRED.** If missing -> skip. Do not generate phonetic variants on-the-fly without a curated dictionary.

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

1. **Structural validity** — Only words present in the phonetic dictionary are modified.
2. **Phonetic plausibility** — The substituted variant should be phonetically similar to the original word in the target language.
3. **Fluency preservation** — The claim should remain pronounceable and semantically interpretable.
4. **Label consistency (input side)** — Gold label preserved; no presupposed target verdict.
5. **Evaluation metrics** — Potency, Correctness Rate, Resilience.

## 8. Example

| Field | Original | Adversarial |
|---|---|---|
| Claim | ਅੰਮ੍ਰਿਤਸਰ ਪੰਜਾਬ ਦਾ ਸ਼ਹਿਰ ਹੈ। | ਅੰਮ੍ਰਿਤਸਰ ਪੰਜਾਬ ਦਾ ਸਹਿਰ ਹੈ। |
| Label | SUP -> (any flip) | Gold retained as SUP; target is generic flip |
| Language | Punjabi (pa) | Punjabi (pa) |
| Edit detail | — | Phonetic variant: "ਸ਼ਹਿਰ" -> "ਸਹਿਰ" |

## 9. Failure Modes / Skip Conditions

1. **No phonetic dictionary** — Skip and log: "Missing phonetic dictionary for {language}."
2. **No applicable words** — If no word in the claim matches a dictionary key, skip.
3. **Language not in target set** — Skip immediately.
