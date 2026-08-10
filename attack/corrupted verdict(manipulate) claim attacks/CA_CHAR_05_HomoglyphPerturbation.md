# Adversarial Attack Description: Homoglyph Perturbation

## 1. Metadata

| Field | Value |
|---|---|
| Attack ID | `CA_CHAR_05_HomoglyphPerturbation` |
| Attack Name | Homoglyph Perturbation |
| Category | `claim_attack` |
| Attack Target | `corrupted_verdict` |
| Edit Granularity | `character` |
| Strategy Type | `rule_based` |
| Access Assumption | black-box (verification + retrieval) |
| Source Paper | (Mamta & Cocarascu, 2025) — FactEval benchmark; catalogued in (Liu et al., 2025) Sec. 5.1.2. Unicode confusables reference: Unicode Security Mechanisms (UTS #39) |

## 2. Description
This attack replaces characters in the claim with visually identical or near-identical homoglyphs drawn from the Unicode Security dictionary. Because the substituted code points map to different tokens or are unrecognized by the model's tokenizer, the claim's representation is corrupted while appearing unchanged to human readers.

## 3. Preconditions / Required Inputs

| Input | Status | Description |
|---|---|---|
| `claim_text` | **required** | The original claim string to be perturbed. |
| `gold_label` | **required** | Original verdict label (`SUP`, `REF`, or `NEI`). |
| `language` | **required** | ISO 639-1/3 code (must be one of: `hi`, `mni`, `te`, `ur`, `pa`, `ta`, `or`, `ml`). |
| `homoglyph_budget` | optional | Maximum number of homoglyph substitutions (default: 1 per word). |
| `unicode_confusables_table` | **required** | A mapping from base characters to their Unicode confusable homoglyphs for the target script. |

## 4. Procedure

1. **Language Detection** — Confirm `language` is in the supported set. If not, skip and log.
2. **Load Confusables** — Load the script-specific confusables table. If no table exists for the target script, skip and log.
3. **Tokenization** — Segment the claim into words (whitespace-delimited tokens).
4. **Candidate Selection** — For each word, identify characters that have at least one homoglyph entry in the confusables table.
5. **Substitution** — Select one candidate character uniformly at random and replace it with its homoglyph. Reassemble the word.
   - For abugidas, avoid substituting a base consonant with a homoglyph that is actually a dependent vowel or combining mark, as this breaks rendering.
   - For Urdu, ensure the homoglyph preserves cursive joining behavior where applicable.
6. **Reassembly** — Replace the original word in the claim string. Preserve whitespace, punctuation, and casing.
7. **Validity Check** — Verify at least one substitution was applied and that the resulting string is valid Unicode. If none succeeded, skip.
8. **Output Packaging** — Populate the JSON output schema.

## 5. Output Schema (JSON)

```json
{
  "attack_id": "CA_CHAR_05_HomoglyphPerturbation",
  "language": "ur",
  "original_claim": "اسلام آباد پاکستان کا دارالحکومت ہے۔",
  "original_evidence": null,
  "adversarial_claim": "اسلام آباد پاکستان کا دارالحکومت ہے۔",
  "adversarial_evidence": null,
  "gold_label": "SUP",
  "target_label": "same_as_gold",
  "edit_granularity": "character",
  "technique_params": {
    "substitution_type": "unicode_homoglyph",
    "substitutions_applied": 1,
    "affected_word": "پاکستان",
    "confusables_source": "UTS39"
  },
  "validity_flags": {
    "fluency_checked": false,
    "label_consistent": true,
    "meaning_preserved": false
  }
}
```

## 6A. Implementation Notes *(engineering constraints only)*

| Language | Script | Execution Blockers / Requirements (tooling only) |
|---|---|---|
| Hindi | Devanagari | **Script-specific confusables table required.** Devanagari has few Latin-style homoglyphs, but digits and some punctuation may have confusables. If no table available, skip. |
| Manipuri | Meitei Mayek / Bengali | **Script-specific confusables table required.** Skip if no table. |
| Telugu | Telugu | **Script-specific confusables table required.** Skip if no table. |
| Urdu | Perso-Arabic (RTL) | **Script-specific confusables table + RTL shaping check required.** Arabic script has many positional homoglyphs; ensure the replacement preserves joining context. Skip if no table. |
| Punjabi | Gurmukhi | **Script-specific confusables table required.** Skip if no table. |
| Tamil | Tamil | **Script-specific confusables table required.** Skip if no table. |
| Odia | Odia | **Script-specific confusables table required.** Skip if no table. |
| Malayalam | Malayalam | **Script-specific confusables table required.** Skip if no table. |

### Generic Mechanical Checklist
- **Grapheme-cluster-aware segmentation available?** Recommended but not strictly required if substitutions are on standalone characters.
- **RTL-safe tokenization/reassembly available?** **REQUIRED** for Urdu only.
- **Morphological analyzer / stemmer?** Not required.
- **Synonym / paraphrase resource or LM?** Not required.
- **Script-specific confusables/homoglyph table?** **REQUIRED** for all languages. If missing → skip. Do not attempt to fabricate homoglyphs heuristically.

## 6B. Empirical Outcome *(output — left blank; filled by evaluation pipeline)*

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

1. **Structural validity** — The adversarial claim differs by one or more homoglyph substitutions.
2. **Visual plausibility** — The substituted character should be visually identical or nearly identical to the original in the target font.
3. **Tokenization impact** — The substitution should map to a different code point (and ideally a different token ID) to corrupt model input.
4. **Label consistency (input side)** — Gold label preserved; no presupposed target verdict.
5. **Evaluation metrics** — Potency, Correctness Rate, Resilience, Human Detectability (should be very low).

## 8. Example

| Field | Original | Adversarial |
|---|---|---|
| Claim | اسلام آباد پاکستان کا دارالحکومت ہے۔ | اسلام آباد پاکستان کا دارالحکومت ہے۔ |
| Label | SUP → (any flip) | Gold retained as SUP; target is generic flip |
| Language | Urdu (ur) | Urdu (ur) |
| Edit detail | — | Homoglyph substitution in `پاکستان` (e.g., replacing a joining character with a visually similar Arabic code point) |

## 9. Failure Modes / Skip Conditions

1. **No confusables table** — Skip and log: "Missing confusables table for {language}."
2. **No applicable candidates** — If no character in the claim has a known homoglyph, skip.
3. **Substitution breaks rendering** — If the homoglyph breaks a conjunct or RTL join, discard candidate. If all fail, skip.
4. **Language not in target set** — Skip immediately.
