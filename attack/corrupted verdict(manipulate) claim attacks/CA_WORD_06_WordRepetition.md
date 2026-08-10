# Adversarial Attack Description: Word Repetition

## 1. Metadata

| Field | Value |
|---|---|
| Attack ID | `CA_WORD_06_WordRepetition` |
| Attack Name | Word Repetition |
| Category | `claim_attack` |
| Attack Target | `corrupted_verdict` |
| Edit Granularity | `word` |
| Strategy Type | `rule_based` |
| Access Assumption | black-box (verification + retrieval) |
| Source Paper | (Mamta & Cocarascu, 2025) — FactEval benchmark; catalogued in (Liu et al., 2025) Sec. 5.1.2 |

## 2. Description
This attack duplicates a randomly selected word in the claim immediately after itself. The local redundancy mimics stuttering or emphasis and can mislead attention mechanisms or n-gram-based features in fact-checking models.

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
3. **Candidate Selection** — If the claim has fewer than 2 words, skip. Otherwise, select one word uniformly at random.
4. **Duplication** — Insert a copy of the selected word immediately after its original position.
5. **Reassembly** — Reconstruct the claim string with the duplicated word. Preserve whitespace around the duplicated pair.
6. **Validity Check** — Verify the adversarial claim differs from the original and that exactly one word was duplicated.
7. **Output Packaging** — Populate the JSON output schema.

## 5. Output Schema (JSON)

```json
{
  "attack_id": "CA_WORD_06_WordRepetition",
  "language": "ta",
  "original_claim": "சென்னை தமிழ்நாட்டின் தலைநகரம்.",
  "original_evidence": null,
  "adversarial_claim": "சென்னை சென்னை தமிழ்நாட்டின் தலைநகரம்.",
  "adversarial_evidence": null,
  "gold_label": "SUP",
  "target_label": "same_as_gold",
  "edit_granularity": "word",
  "technique_params": {
    "repetition_type": "single_word_duplicate",
    "duplicated_word": "சென்னை",
    "position": 0
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
| Urdu | Perso-Arabic (RTL) | **RTL-safe reassembly required.** Duplicating an RTL word preserves rendering with standard string ops. |
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

1. **Structural validity** — Exactly one word is duplicated; no other changes.
2. **Position validity** — The duplicate appears immediately after the original instance.
3. **Label consistency (input side)** — Gold label preserved; no presupposed target verdict.
4. **Evaluation metrics** — Potency, Correctness Rate, Resilience.

## 8. Example

| Field | Original | Adversarial |
|---|---|---|
| Claim | சென்னை தமிழ்நாட்டின் தலைநகரம். | சென்னை சென்னை தமிழ்நாட்டின் தலைநகரம். |
| Label | SUP -> (any flip) | Gold retained as SUP; target is generic flip |
| Language | Tamil (ta) | Tamil (ta) |
| Edit detail | — | Word "சென்னை" duplicated after itself |

## 9. Failure Modes / Skip Conditions

1. **Claim too short** — If the claim has fewer than 2 words, skip.
2. **Language not in target set** — Skip immediately.
