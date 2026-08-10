# Adversarial Attack Description: Jumbling

## 1. Metadata

| Field | Value |
|---|---|
| Attack ID | `CA_WORD_03_Jumbling` |
| Attack Name | Jumbling |
| Category | `claim_attack` |
| Attack Target | `corrupted_verdict` |
| Edit Granularity | `word` |
| Strategy Type | `rule_based` |
| Access Assumption | black-box (verification + retrieval) |
| Source Paper | (Mamta & Cocarascu, 2025) — FactEval benchmark; catalogued in (Liu et al., 2025) Sec. 5.1.2 |

## 2. Description
This attack perturbs a claim by randomly changing the order of its words. The bag-of-words content is preserved, but syntactic structure is destroyed. It tests whether the fact-checking model relies on word-order cues and grammatical structure or merely on shallow lexical overlap with evidence.

## 3. Preconditions / Required Inputs

| Input | Status | Description |
|---|---|---|
| `claim_text` | **required** | The original claim string to be perturbed. |
| `gold_label` | **required** | Original verdict label (SUP, REF, or NEI). |
| `language` | **required** | ISO 639-1/3 code (must be one of: hi, mni, te, ur, pa, ta, or, ml). |
| `tokenizer` | optional | Word tokenizer for the target language. |

## 4. Procedure

1. **Language Detection** — Confirm `language` is in the supported set. If not, skip and log.
2. **Tokenization** — Split the claim into a list of words (whitespace-delimited). Preserve punctuation as separate tokens or attach them consistently.
3. **Shuffle** — Randomly shuffle the word list using a uniform random permutation.
4. **Reassembly** — Join the shuffled words with single spaces to form the adversarial claim.
   - For Urdu (RTL), ensure the overall text direction remains RTL; individual words retain internal order.
5. **Validity Check** — Verify the adversarial claim differs from the original. If the shuffle reproduces the original order, reshuffle or skip.
6. **Output Packaging** — Populate the JSON output schema.

## 5. Output Schema (JSON)

```json
{
  "attack_id": "CA_WORD_03_Jumbling",
  "language": "te",
  "original_claim": "హైదరాబాద్ తెలంగాణ రాజధాని.",
  "original_evidence": null,
  "adversarial_claim": "రాజధాని తెలంగాణ హైదరాబాద్.",
  "adversarial_evidence": null,
  "gold_label": "SUP",
  "target_label": "same_as_gold",
  "edit_granularity": "word",
  "technique_params": {
    "shuffle_type": "uniform_random",
    "word_order_preserved": false
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
| Urdu | Perso-Arabic (RTL) | **RTL-safe reassembly required.** Shuffling must not break individual word shapes. |
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

1. **Structural validity** — All original words are preserved exactly; only their order changes.
2. **Syntactic disruption** — The shuffled claim should be grammatically incorrect.
3. **Label consistency (input side)** — Gold label preserved; no presupposed target verdict.
4. **Evaluation metrics** — Potency, Correctness Rate, Resilience.

## 8. Example

| Field | Original | Adversarial |
|---|---|---|
| Claim | హైదరాబాద్ తెలంగాణ రాజధాని. | రాజధాని తెలంగాణ హైదరాబాద్. |
| Label | SUP -> (any flip) | Gold retained as SUP; target is generic flip |
| Language | Telugu (te) | Telugu (te) |
| Edit detail | — | Uniform random shuffle of word order |

## 9. Failure Modes / Skip Conditions

1. **Claim too short** — If the claim has fewer than 3 words, skip.
2. **Shuffle reproduces original** — If the random permutation yields the original order, reshuffle once; if it persists, skip.
3. **Language not in target set** — Skip immediately.
