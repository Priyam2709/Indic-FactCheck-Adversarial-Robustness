# Adversarial Attack Description: Typos

## 1. Metadata

| Field | Value |
|---|---|
| Attack ID | `CA_WORD_04_Typos` |
| Attack Name | Typos |
| Category | `claim_attack` |
| Attack Target | `corrupted_verdict` |
| Edit Granularity | `word` |
| Strategy Type | `rule_based` |
| Access Assumption | black-box (verification + retrieval) |
| Source Paper | (Mamta & Cocarascu, 2025) — FactEval benchmark; catalogued in (Liu et al., 2025) Sec. 5.1.2 |

## 2. Description
This attack introduces common typographical errors at the word level by replacing words with their frequent misspellings or keyboard-proximity variants. Unlike character-level swapping, it operates on whole-word substitutions drawn from a typo dictionary, preserving the intended meaning to a human reader while corrupting exact-match tokenization.

## 3. Preconditions / Required Inputs

| Input | Status | Description |
|---|---|---|
| `claim_text` | **required** | The original claim string to be perturbed. |
| `gold_label` | **required** | Original verdict label (SUP, REF, or NEI). |
| `language` | **required** | ISO 639-1/3 code (must be one of: hi, mni, te, ur, pa, ta, or, ml). |
| `typo_dictionary` | **required** | A mapping from correctly spelled words to common misspellings for the target language/script. |

## 4. Procedure

1. **Language Detection** — Confirm `language` is in the supported set. If not, skip and log.
2. **Load Typo Dictionary** — Load the language-specific typo dictionary. If no dictionary exists, skip and log.
3. **Candidate Scan** — Scan the claim for words that appear as keys in the typo dictionary.
   - If no candidates are found, skip the instance.
4. **Substitution** — Select one candidate word uniformly at random and replace it with one of its listed misspellings.
5. **Reassembly** — Reconstruct the claim string. Preserve surrounding whitespace and punctuation.
6. **Validity Check** — Verify the claim text has changed. If no substitution was applied, skip.
7. **Output Packaging** — Populate the JSON output schema.

## 5. Output Schema (JSON)

```json
{
  "attack_id": "CA_WORD_04_Typos",
  "language": "hi",
  "original_claim": "भारत की राजधानी दिल्ली है।",
  "original_evidence": null,
  "adversarial_claim": "भारत की राजधानी दिल्ली है।",
  "adversarial_evidence": null,
  "gold_label": "SUP",
  "target_label": "same_as_gold",
  "edit_granularity": "word",
  "technique_params": {
    "substitution_type": "typo_dictionary",
    "original_word": "दिल्ली",
    "typo_variant": "दिल्ली",
    "typos_applied": 1
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
| Hindi | Devanagari | **Typo dictionary required.** If no curated typo list, skip. |
| Manipuri | Meitei Mayek / Bengali | **Typo dictionary required.** If no dictionary, skip. |
| Telugu | Telugu | **Typo dictionary required.** If no dictionary, skip. |
| Urdu | Perso-Arabic (RTL) | **Typo dictionary required.** If no dictionary, skip. |
| Punjabi | Gurmukhi | **Typo dictionary required.** If no dictionary, skip. |
| Tamil | Tamil | **Typo dictionary required.** If no dictionary, skip. |
| Odia | Odia | **Typo dictionary required.** If no dictionary, skip. |
| Malayalam | Malayalam | **Typo dictionary required.** If no dictionary, skip. |

### Generic Mechanical Checklist
- **Typo dictionary for the language?** **REQUIRED.** If missing -> skip.

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

1. **Structural validity** — Only words present in the typo dictionary are modified.
2. **Fluency preservation** — The typo variant should be a plausible human misspelling.
3. **Label consistency (input side)** — Gold label preserved; no presupposed target verdict.
4. **Evaluation metrics** — Potency, Correctness Rate, Resilience.

## 8. Example

| Field | Original | Adversarial |
|---|---|---|
| Claim | भारत की राजधानी दिल्ली है। | भारत की राजधानी दिल्ली है। |
| Label | SUP -> (any flip) | Gold retained as SUP; target is generic flip |
| Language | Hindi (hi) | Hindi (hi) |
| Edit detail | — | Typo substitution in word "दिल्ली" |

## 9. Failure Modes / Skip Conditions

1. **No typo dictionary** — Skip and log: "Missing typo dictionary for {language}."
2. **No applicable words** — If no word in the claim matches a dictionary key, skip.
3. **Language not in target set** — Skip immediately.
