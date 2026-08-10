# Adversarial Attack Description: Contractions

## 1. Metadata

| Field | Value |
|---|---|
| Attack ID | `CA_WORD_02_Contractions` |
| Attack Name | Contractions |
| Category | `claim_attack` |
| Attack Target | `corrupted_verdict` |
| Edit Granularity | `word` |
| Strategy Type | `rule_based` |
| Access Assumption | black-box (verification + retrieval) |
| Source Paper | (Mamta & Cocarascu, 2025) — FactEval benchmark; catalogued in (Liu et al., 2025) Sec. 5.1.2 |

## 2. Description
This attack replaces word sequences in the claim with their contracted forms. By introducing informal shortened forms, it tests whether the fact-checking model handles colloquial or compressed orthography correctly, potentially causing tokenization mismatches that lead to incorrect verdicts.

## 3. Preconditions / Required Inputs

| Input | Status | Description |
|---|---|---|
| `claim_text` | **required** | The original claim string to be perturbed. |
| `gold_label` | **required** | Original verdict label (SUP, REF, or NEI). |
| `language` | **required** | ISO 639-1/3 code (must be one of: hi, mni, te, ur, pa, ta, or, ml). |
| `contraction_table` | **required** | A language-specific mapping from full phrases to their contracted forms. |

## 4. Procedure

1. **Language Detection** — Confirm `language` is in the supported set. If not, skip and log.
2. **Load Contraction Table** — Load the contraction mapping for the target language. If no table exists, skip and log.
3. **Candidate Scan** — Scan the claim for any multi-word phrase that exists as a key in the contraction table.
   - If no candidates are found, skip the instance.
4. **Substitution** — Select one candidate phrase uniformly at random and replace it with its contracted form.
5. **Reassembly** — Reconstruct the claim string. Preserve surrounding whitespace and punctuation.
6. **Validity Check** — Verify the claim text has changed. If no substitution was applied, skip.
7. **Output Packaging** — Populate the JSON output schema.

## 5. Output Schema (JSON)

```json
{
  "attack_id": "CA_WORD_02_Contractions",
  "language": "hi",
  "original_claim": "यह सच नहीं है कि वह आएगा।",
  "original_evidence": null,
  "adversarial_claim": "यह सच नहीं'है कि वह आएगा।",
  "adversarial_evidence": null,
  "gold_label": "REF",
  "target_label": "same_as_gold",
  "edit_granularity": "word",
  "technique_params": {
    "substitution_type": "contraction",
    "original_phrase": "नहीं है",
    "contracted_form": "नहीं'है",
    "contractions_applied": 1
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
| Hindi | Devanagari | **Contraction table required.** Hindi has limited written contractions. If no curated table, skip. |
| Manipuri | Meitei Mayek / Bengali | **Contraction table required.** If no table, skip. |
| Telugu | Telugu | **Contraction table required.** If no table, skip. |
| Urdu | Perso-Arabic (RTL) | **Contraction table required.** If no table, skip. |
| Punjabi | Gurmukhi | **Contraction table required.** If no table, skip. |
| Tamil | Tamil | **Contraction table required.** If no table, skip. |
| Odia | Odia | **Contraction table required.** If no table, skip. |
| Malayalam | Malayalam | **Contraction table required.** If no table, skip. |

### Generic Mechanical Checklist
- **Contraction table for the language?** **REQUIRED.** If missing -> skip.

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

1. **Structural validity** — Only full phrases present in the contraction table are modified.
2. **Fluency preservation** — The contracted form should be a recognized shortened form.
3. **Label consistency (input side)** — Gold label preserved; no presupposed target verdict.
4. **Evaluation metrics** — Potency, Correctness Rate, Resilience.

## 8. Example

| Field | Original | Adversarial |
|---|---|---|
| Claim | यह सच नहीं है कि वह आएगा। | यह सच नहीं'है कि वह आएगा। |
| Label | REF -> (any flip) | Gold retained as REF; target is generic flip |
| Language | Hindi (hi) | Hindi (hi) |
| Edit detail | — | Contraction of phrase "नहीं है" |

## 9. Failure Modes / Skip Conditions

1. **No contraction table** — Skip and log: "Missing contraction table for {language}."
2. **No applicable phrases** — If no phrase in the claim matches a contraction key, skip.
3. **Language not in target set** — Skip immediately.
