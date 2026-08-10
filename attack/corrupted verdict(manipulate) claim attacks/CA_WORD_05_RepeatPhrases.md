# Adversarial Attack Description: Repeat Phrases

## 1. Metadata

| Field | Value |
|---|---|
| Attack ID | `CA_WORD_05_RepeatPhrases` |
| Attack Name | Repeat Phrases |
| Category | `claim_attack` |
| Attack Target | `corrupted_verdict` |
| Edit Granularity | `word` |
| Strategy Type | `rule_based` |
| Access Assumption | black-box (verification + retrieval) |
| Source Paper | (Mamta & Cocarascu, 2025) — FactEval benchmark; catalogued in (Liu et al., 2025) Sec. 5.1.2 |

## 2. Description
This attack appends the first quarter of the claim to the end of the original claim. The added redundancy can confuse attention-based fact-checking models or dilute semantic signals, potentially causing misclassification while the claim remains logically coherent to human readers.

## 3. Preconditions / Required Inputs

| Input | Status | Description |
|---|---|---|
| `claim_text` | **required** | The original claim string to be perturbed. |
| `gold_label` | **required** | Original verdict label (SUP, REF, or NEI). |
| `language` | **required** | ISO 639-1/3 code (must be one of: hi, mni, te, ur, pa, ta, or, ml). |
| `tokenizer` | optional | Word tokenizer for the target language. |

## 4. Procedure

1. **Language Detection** — Confirm `language` is in the supported set. If not, skip and log.
2. **Tokenization** — Split the claim into a list of words (whitespace-delimited).
3. **Length Check** — If the claim has fewer than 4 words, skip.
4. **Extract Prefix** — Take the first quarter of the word list, rounded down.
5. **Append** — Concatenate the original claim, a space, and the extracted prefix.
6. **Validity Check** — Verify the adversarial claim is longer than the original. If not, skip.
7. **Output Packaging** — Populate the JSON output schema.

## 5. Output Schema (JSON)

```json
{
  "attack_id": "CA_WORD_05_RepeatPhrases",
  "language": "hi",
  "original_claim": "भारत की राजधानी दिल्ली है।",
  "original_evidence": null,
  "adversarial_claim": "भारत की राजधानी दिल्ली है। भारत",
  "adversarial_evidence": null,
  "gold_label": "SUP",
  "target_label": "same_as_gold",
  "edit_granularity": "word",
  "technique_params": {
    "repetition_type": "prefix_append",
    "prefix_length_words": 1,
    "original_length_words": 5
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
| Hindi | Devanagari | **Word tokenizer required.** Whitespace tokenization is sufficient. |
| Manipuri | Meitei Mayek / Bengali | **Word tokenizer required.** Whitespace tokenization is sufficient. |
| Telugu | Telugu | **Word tokenizer required.** Whitespace tokenization is sufficient. |
| Urdu | Perso-Arabic (RTL) | **RTL-safe reassembly required.** Appending to RTL must preserve directionality. |
| Punjabi | Gurmukhi | **Word tokenizer required.** Whitespace tokenization is sufficient. |
| Tamil | Tamil | **Word tokenizer required.** Whitespace tokenization is sufficient. |
| Odia | Odia | **Word tokenizer required.** Whitespace tokenization is sufficient. |
| Malayalam | Malayalam | **Word tokenizer required.** Whitespace tokenization is sufficient. |

### Generic Mechanical Checklist
- **RTL-safe tokenization/reassembly available?** Recommended for Urdu only.

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

1. **Structural validity** — The original claim is preserved in full, followed by an appended prefix.
2. **Prefix length** — The prefix must be exactly the first quarter (rounded down) of the word count.
3. **Label consistency (input side)** — Gold label preserved; no presupposed target verdict.
4. **Evaluation metrics** — Potency, Correctness Rate, Resilience.

## 8. Example

| Field | Original | Adversarial |
|---|---|---|
| Claim | भारत की राजधानी दिल्ली है। | भारत की राजधानी दिल्ली है। भारत |
| Label | SUP -> (any flip) | Gold retained as SUP; target is generic flip |
| Language | Hindi (hi) | Hindi (hi) |
| Edit detail | — | First quarter (1 word: भारत) appended to end |

## 9. Failure Modes / Skip Conditions

1. **Claim too short** — If the claim has fewer than 4 words, skip.
2. **Language not in target set** — Skip immediately.
