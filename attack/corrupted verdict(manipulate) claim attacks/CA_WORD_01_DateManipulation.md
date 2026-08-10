# Adversarial Attack Description: Date Manipulation

## 1. Metadata

| Field | Value |
|---|---|
| Attack ID | `CA_WORD_01_DateManipulation` |
| Attack Name | Date Manipulation |
| Category | `claim_attack` |
| Attack Target | `corrupted_verdict` |
| Edit Granularity | `word` |
| Strategy Type | `rule_based` |
| Access Assumption | black-box (verification + retrieval) |
| Source Paper | (Hidey et al., 2020) — DeSePtion; benchmarked in (Mamta & Cocarascu, 2025); catalogued in (Liu et al., 2025) Sec. 5.1.2 |

## 2. Description
This attack manipulates temporal expressions in a claim using heuristics such as arithmetic date shifting, range modification, or verbalization changes. By altering dates without changing surrounding context, it exploits weaknesses in temporal reasoning and numeric grounding within fact-checking models.

## 3. Preconditions / Required Inputs

| Input | Status | Description |
|---|---|---|
| `claim_text` | **required** | The original claim string to be perturbed. |
| `gold_label` | **required** | Original verdict label (SUP, REF, or NEI). |
| `language` | **required** | ISO 639-1/3 code (must be one of: hi, mni, te, ur, pa, ta, or, ml). |
| `date_entities` | **required** | List of date spans detected in the claim. |
| `date_manipulation_heuristic` | optional | One of arithmetic, range, verbalization (default: random valid heuristic). |
| `date_parser` | optional | Language-aware date parser / NER tool for the target language. |

## 4. Procedure

1. **Language Detection** — Confirm `language` is in the supported set. If not, skip and log.
2. **Date Extraction** — Run a date-aware NER or regex parser over the claim to identify all temporal expressions.
   - If no date entities are found, skip the instance.
   - If the date parser does not support the target language, skip and log.
3. **Heuristic Selection** — Randomly select one detected date entity and one applicable heuristic:
   - **Arithmetic**: Add or subtract a small integer to/from a year or day.
   - **Range**: Widen or narrow a date range.
   - **Verbalization**: Replace a numeric date with a verbalized form or vice versa.
4. **Claim Reconstruction** — Replace the original date span with the manipulated date string. Preserve all surrounding text.
5. **Validity Check** — Verify that the manipulated date is syntactically valid and that the claim text has actually changed. If invalid or null, skip.
6. **Output Packaging** — Populate the JSON output schema.

## 5. Output Schema (JSON)

```json
{
  "attack_id": "CA_WORD_01_DateManipulation",
  "language": "hi",
  "original_claim": "भारत ने 15 अगस्त 1947 को स्वतंत्रता प्राप्त की।",
  "original_evidence": null,
  "adversarial_claim": "भारत ने 15 अगस्त 1957 को स्वतंत्रता प्राप्त की।",
  "adversarial_evidence": null,
  "gold_label": "SUP",
  "target_label": "same_as_gold",
  "edit_granularity": "word",
  "technique_params": {
    "manipulation_type": "arithmetic",
    "original_date": "1947",
    "modified_date": "1957",
    "shift_amount": 10
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
| Hindi | Devanagari | **Date parser / NER required.** Hindi dates may use Devanagari digits or Arabic numerals. If no parser, skip. |
| Manipuri | Meitei Mayek / Bengali | **Date parser / NER required.** If no parser, skip. |
| Telugu | Telugu | **Date parser / NER required.** If no parser, skip. |
| Urdu | Perso-Arabic (RTL) | **Date parser / NER required.** Urdu dates may use Hijri or Gregorian calendars. If no parser, skip. |
| Punjabi | Gurmukhi | **Date parser / NER required.** If no parser, skip. |
| Tamil | Tamil | **Date parser / NER required.** If no parser, skip. |
| Odia | Odia | **Date parser / NER required.** If no parser, skip. |
| Malayalam | Malayalam | **Date parser / NER required.** If no parser, skip. |

### Generic Mechanical Checklist
- **Date parser / NER for the language?** **REQUIRED.** If missing -> skip.

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

1. **Structural validity** — Only date entities are modified.
2. **Date validity** — The manipulated date must be syntactically valid.
3. **Fluency preservation** — The claim remains grammatically correct.
4. **Label consistency (input side)** — Gold label preserved; no presupposed target verdict.
5. **Evaluation metrics** — Potency, Correctness Rate, Resilience.

## 8. Example

| Field | Original | Adversarial |
|---|---|---|
| Claim | भारत ने 15 अगस्त 1947 को स्वतंत्रता प्राप्त की। | भारत ने 15 अगस्त 1957 को स्वतंत्रता प्राप्त की। |
| Label | SUP -> (any flip) | Gold retained as SUP; target is generic flip |
| Language | Hindi (hi) | Hindi (hi) |
| Edit detail | — | Arithmetic shift: 1947 -> 1957 (+10 years) |

## 9. Failure Modes / Skip Conditions

1. **No date entities found** — Skip and log: "No date entities detected."
2. **Missing date parser** — Skip and log: "Missing date parser for {language}."
3. **Invalid manipulated date** — If the heuristic produces an impossible date, discard and try another candidate. If all fail, skip.
4. **Language not in target set** — Skip immediately.
