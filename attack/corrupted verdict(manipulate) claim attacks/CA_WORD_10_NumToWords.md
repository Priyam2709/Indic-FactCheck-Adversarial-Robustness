# Adversarial Attack Description: Num To Words

## 1. Metadata

| Field | Value |
|---|---|
| Attack ID | `CA_WORD_10_NumToWords` |
| Attack Name | Num To Words |
| Category | `claim_attack` |
| Attack Target | `corrupted_verdict` |
| Edit Granularity | `word` |
| Strategy Type | `rule_based` |
| Access Assumption | black-box (verification + retrieval) |
| Source Paper | (Mamta & Cocarascu, 2025) — FactEval benchmark; catalogued in (Liu et al., 2025) Sec. 5.1.2 |

## 2. Description
This attack converts all numerical digits in the claim to their word equivalents. It tests whether the fact-checking model robustly handles numeric reasoning across different textual representations or relies on exact digit matching.

## 3. Preconditions / Required Inputs

| Input | Status | Description |
|---|---|---|
| `claim_text` | **required** | The original claim string to be perturbed. |
| `gold_label` | **required** | Original verdict label (SUP, REF, or NEI). |
| `language` | **required** | ISO 639-1/3 code (must be one of: hi, mni, te, ur, pa, ta, or, ml). |
| `num2words_converter` | **required** | A library or function that converts Arabic numerals to words in the target language. |

## 4. Procedure

1. **Language Detection** — Confirm `language` is in the supported set. If not, skip and log.
2. **Load Converter** — Initialize the num2words converter for the target language. If no converter exists, skip and log.
3. **Digit Detection** — Scan the claim for sequences of Arabic numerals (0-9). Also detect numerals in native script digits if the converter supports them.
   - If no digits are found, skip the instance.
4. **Conversion** — For each detected numeral, convert it to its word equivalent.
5. **Reassembly** — Replace each numeral in the claim with its word form. Preserve surrounding whitespace and punctuation.
6. **Validity Check** — Verify at least one numeral was converted. If none were converted, skip.
7. **Output Packaging** — Populate the JSON output schema.

## 5. Output Schema (JSON)

```json
{
  "attack_id": "CA_WORD_10_NumToWords",
  "language": "te",
  "original_claim": "2024 ఒలింపిక్ క్రీడలు ప్యారిస్‌లో జరుగుతాయి.",
  "original_evidence": null,
  "adversarial_claim": "రెండు వేల ఇరవై నాలుగు ఒలింపిక్ క్రీడలు ప్యారిస్‌లో జరుగుతాయి.",
  "adversarial_evidence": null,
  "gold_label": "SUP",
  "target_label": "same_as_gold",
  "edit_granularity": "word",
  "technique_params": {
    "conversion_type": "num2words",
    "numerals_converted": ["2024"],
    "word_forms": ["రెండు వేల ఇరవై నాలుగు"]
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
| Hindi | Devanagari | **num2words converter required.** Must handle Hindi number words. If unavailable, skip. |
| Manipuri | Meitei Mayek / Bengali | **num2words converter required.** If unavailable, skip. |
| Telugu | Telugu | **num2words converter required.** If unavailable, skip. |
| Urdu | Perso-Arabic (RTL) | **num2words converter required.** If unavailable, skip. |
| Punjabi | Gurmukhi | **num2words converter required.** If unavailable, skip. |
| Tamil | Tamil | **num2words converter required.** If unavailable, skip. |
| Odia | Odia | **num2words converter required.** If unavailable, skip. |
| Malayalam | Malayalam | **num2words converter required.** If unavailable, skip. |

### Generic Mechanical Checklist
- **num2words converter for the language?** **REQUIRED.** If missing -> skip.

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

1. **Structural validity** — All numerals in the claim are converted to words.
2. **Completeness** — Every Arabic numeral (and native-script numeral, if supported) must be converted.
3. **Fluency preservation** — The resulting claim should be grammatically correct.
4. **Label consistency (input side)** — Gold label preserved; no presupposed target verdict.
5. **Evaluation metrics** — Potency, Correctness Rate, Resilience.

## 8. Example

| Field | Original | Adversarial |
|---|---|---|
| Claim | 2024 ఒలింపిక్ క్రీడలు ప్యారిస్‌లో జరుగుతాయి. | రెండు వేల ఇరవై నాలుగు ఒలింపిక్ క్రీడలు ప్యారిస్‌లో జరుగుతాయి. |
| Label | SUP -> (any flip) | Gold retained as SUP; target is generic flip |
| Language | Telugu (te) | Telugu (te) |
| Edit detail | — | "2024" -> "రెండు వేల ఇరవై నాలుగు" |

## 9. Failure Modes / Skip Conditions

1. **No num2words converter** — Skip and log: "Missing num2words converter for {language}."
2. **No numerals found** — If the claim contains no digit sequences, skip.
3. **Converter fails on a numeral** — If the converter cannot handle a specific number, skip that numeral. If all numerals fail, skip.
4. **Language not in target set** — Skip immediately.
