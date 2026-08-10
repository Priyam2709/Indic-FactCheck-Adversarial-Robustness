# Adversarial Attack Description: Expansions

## 1. Metadata

| Field | Value |
|---|---|
| Attack ID | `CA_WORD_09_Expansions` |
| Attack Name | Expansions |
| Category | `claim_attack` |
| Attack Target | `corrupted_verdict` |
| Edit Granularity | `word` |
| Strategy Type | `rule_based` |
| Access Assumption | black-box (verification + retrieval) |
| Source Paper | (Mamta & Cocarascu, 2025) — FactEval benchmark; catalogued in (Liu et al., 2025) Sec. 5.1.2 |

## 2. Description
This attack replaces contracted forms in the claim with their full, expanded versions. It is the inverse of the Contractions attack and tests whether the fact-checking model is sensitive to formal versus informal orthographic variants.

## 3. Preconditions / Required Inputs

| Input | Status | Description |
|---|---|---|
| `claim_text` | **required** | The original claim string to be perturbed. |
| `gold_label` | **required** | Original verdict label (SUP, REF, or NEI). |
| `language` | **required** | ISO 639-1/3 code (must be one of: hi, mni, te, ur, pa, ta, or, ml). |
| `expansion_table` | **required** | A language-specific mapping from contracted forms to their full phrases. |

## 4. Procedure

1. **Language Detection** — Confirm `language` is in the supported set. If not, skip and log.
2. **Load Expansion Table** — Load the expansion mapping for the target language. If no table exists, skip and log.
3. **Candidate Scan** — Scan the claim for any contracted form that exists as a key in the expansion table.
   - If no candidates are found, skip the instance.
4. **Substitution** — Select one candidate contracted form uniformly at random and replace it with its expanded phrase.
5. **Reassembly** — Reconstruct the claim string. Preserve surrounding whitespace and punctuation.
6. **Validity Check** — Verify the claim text has changed. If no substitution was applied, skip.
7. **Output Packaging** — Populate the JSON output schema.

## 5. Output Schema (JSON)

```json
{
  "attack_id": "CA_WORD_09_Expansions",
  "language": "ur",
  "original_claim": "وہ نہیں'جائے گا۔",
  "original_evidence": null,
  "adversarial_claim": "وہ نہیں جائے گا۔",
  "adversarial_evidence": null,
  "gold_label": "REF",
  "target_label": "same_as_gold",
  "edit_granularity": "word",
  "technique_params": {
    "substitution_type": "expansion",
    "contracted_form": "نہیں'جائے",
    "expanded_form": "نہیں جائے",
    "expansions_applied": 1
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
| Hindi | Devanagari | **Expansion table required.** If no curated table, skip. |
| Manipuri | Meitei Mayek / Bengali | **Expansion table required.** If no table, skip. |
| Telugu | Telugu | **Expansion table required.** If no table, skip. |
| Urdu | Perso-Arabic (RTL) | **Expansion table required.** If no table, skip. |
| Punjabi | Gurmukhi | **Expansion table required.** If no table, skip. |
| Tamil | Tamil | **Expansion table required.** If no table, skip. |
| Odia | Odia | **Expansion table required.** If no table, skip. |
| Malayalam | Malayalam | **Expansion table required.** If no table, skip. |

### Generic Mechanical Checklist
- **Expansion table for the language?** **REQUIRED.** If missing -> skip.

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

1. **Structural validity** — Only contracted forms present in the expansion table are modified.
2. **Fluency preservation** — The expanded form should be grammatically correct in context.
3. **Label consistency (input side)** — Gold label preserved; no presupposed target verdict.
4. **Evaluation metrics** — Potency, Correctness Rate, Resilience.

## 8. Example

| Field | Original | Adversarial |
|---|---|---|
| Claim | وہ نہیں'جائے گا۔ | وہ نہیں جائے گا۔ |
| Label | REF -> (any flip) | Gold retained as REF; target is generic flip |
| Language | Urdu (ur) | Urdu (ur) |
| Edit detail | — | Expansion of contracted form "نہیں'جائے" -> "نہیں جائے" |

## 9. Failure Modes / Skip Conditions

1. **No expansion table** — Skip and log: "Missing expansion table for {language}."
2. **No applicable contractions** — If no contracted form in the claim matches a table key, skip.
3. **Language not in target set** — Skip immediately.
