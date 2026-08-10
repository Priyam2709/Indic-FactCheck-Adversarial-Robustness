# Adversarial Attack Description: Tautology

## 1. Metadata

| Field | Value |
|---|---|
| Attack ID | `CA_WORD_07_Tautology` |
| Attack Name | Tautology |
| Category | `claim_attack` |
| Attack Target | `corrupted_verdict` |
| Edit Granularity | `word` |
| Strategy Type | `rule_based` |
| Access Assumption | black-box (verification + retrieval) |
| Source Paper | (Mamta & Cocarascu, 2025) — FactEval benchmark; catalogued in (Liu et al., 2025) Sec. 5.1.2 |

## 2. Description
This attack appends a logically vacuous tautological phrase to the end of the claim. By injecting semantically empty but grammatically coherent text, it dilutes the semantic signal and can confuse models that rely on sentence-level representations or attention over the full claim text.

## 3. Preconditions / Required Inputs

| Input | Status | Description |
|---|---|---|
| `claim_text` | **required** | The original claim string to be perturbed. |
| `gold_label` | **required** | Original verdict label (SUP, REF, or NEI). |
| `language` | **required** | ISO 639-1/3 code (must be one of: hi, mni, te, ur, pa, ta, or, ml). |
| `tautology_phrase` | **required** | A language-specific tautological phrase equivalent to "and true is true". |

## 4. Procedure

1. **Language Detection** — Confirm `language` is in the supported set. If not, skip and log.
2. **Load Tautology Phrase** — Retrieve the localized tautology phrase for the target language. If no localized phrase is available, skip and log.
3. **Append** — Concatenate the original claim, a space, and the tautology phrase repeated three times.
4. **Reassembly** — Ensure proper spacing and punctuation.
5. **Validity Check** — Verify the adversarial claim is longer than the original. If not, skip.
6. **Output Packaging** — Populate the JSON output schema.

## 5. Output Schema (JSON)

```json
{
  "attack_id": "CA_WORD_07_Tautology",
  "language": "hi",
  "original_claim": "भारत की राजधानी दिल्ली है।",
  "original_evidence": null,
  "adversarial_claim": "भारत की राजधानी दिल्ली है। और सच सच है और सच सच है और सच सच है।",
  "adversarial_evidence": null,
  "gold_label": "SUP",
  "target_label": "same_as_gold",
  "edit_granularity": "word",
  "technique_params": {
    "append_type": "tautology_x3",
    "tautology_phrase": "और सच सच है",
    "repetitions": 3
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
| Hindi | Devanagari | **Localized tautology phrase required.** If no curated phrase, skip. Do not use English verbatim. |
| Manipuri | Meitei Mayek / Bengali | **Localized tautology phrase required.** Skip if unavailable. |
| Telugu | Telugu | **Localized tautology phrase required.** Skip if unavailable. |
| Urdu | Perso-Arabic (RTL) | **Localized tautology phrase required.** Skip if unavailable. |
| Punjabi | Gurmukhi | **Localized tautology phrase required.** Skip if unavailable. |
| Tamil | Tamil | **Localized tautology phrase required.** Skip if unavailable. |
| Odia | Odia | **Localized tautology phrase required.** Skip if unavailable. |
| Malayalam | Malayalam | **Localized tautology phrase required.** Skip if unavailable. |

### Generic Mechanical Checklist
- **Localized tautology phrase?** **REQUIRED.** If missing -> skip.

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

1. **Structural validity** — The original claim is preserved in full, followed by exactly three repetitions of the tautology phrase.
2. **Localization** — The tautology phrase must be in the same language/script as the claim.
3. **Label consistency (input side)** — Gold label preserved; no presupposed target verdict.
4. **Evaluation metrics** — Potency, Correctness Rate, Resilience.

## 8. Example

| Field | Original | Adversarial |
|---|---|---|
| Claim | भारत की राजधानी दिल्ली है। | भारत की राजधानी दिल्ली है। और सच सच है और सच सच है और सच सच है। |
| Label | SUP -> (any flip) | Gold retained as SUP; target is generic flip |
| Language | Hindi (hi) | Hindi (hi) |
| Edit detail | — | Tautology phrase "और सच सच है" appended three times |

## 9. Failure Modes / Skip Conditions

1. **No localized tautology phrase** — Skip and log: "Missing tautology phrase for {language}."
2. **Language not in target set** — Skip immediately.
