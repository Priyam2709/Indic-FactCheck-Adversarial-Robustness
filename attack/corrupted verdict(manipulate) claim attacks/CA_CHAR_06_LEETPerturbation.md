# Adversarial Attack Description: LEET Perturbation

## 1. Metadata

| Field | Value |
|---|---|
| Attack ID | `CA_CHAR_06_LEETPerturbation` |
| Attack Name | LEET Perturbation |
| Category | `claim_attack` |
| Attack Target | `corrupted_verdict` |
| Edit Granularity | `character` |
| Strategy Type | `rule_based` |
| Access Assumption | black-box (verification + retrieval) |
| Source Paper | (Mamta & Cocarascu, 2025) — FactEval benchmark; catalogued in (Liu et al., 2025) Sec. 5.1.2 |

## 2. Description
This attack replaces letters with visually similar symbols using a predefined LEET-style dictionary. Originally developed for Latin-script alphanumeric substitution, the attack can be adapted to any script by mapping characters to visually similar glyphs or digits available in that script's Unicode block, thereby corrupting tokenization while preserving surface readability.

## 3. Preconditions / Required Inputs

| Input | Status | Description |
|---|---|---|
| `claim_text` | **required** | The original claim string to be perturbed. |
| `gold_label` | **required** | Original verdict label (`SUP`, `REF`, or `NEI`). |
| `language` | **required** | ISO 639-1/3 code (must be one of: `hi`, `mni`, `te`, `ur`, `pa`, `ta`, `or`, `ml`). |
| `leet_budget` | optional | Maximum LEET substitutions per claim (default: 1 per word). |
| `leet_dictionary` | **required** | A mapping from script characters to visually similar replacement characters or digits for the target language/script. |

## 4. Procedure

1. **Language Detection** — Confirm `language` is in the supported set. If not, skip and log.
2. **Load LEET Dictionary** — Load the script-specific LEET mapping. If no dictionary exists for the target script, skip and log.
3. **Tokenization** — Segment the claim into words (whitespace-delimited tokens).
4. **Candidate Selection** — For each word, identify characters that have at least one LEET replacement in the dictionary.
5. **Substitution** — Select one candidate character uniformly at random and replace it with its LEET equivalent. Reassemble the word.
   - For abugidas, ensure the replacement character does not break a conjunct or combine invalidly with adjacent marks.
   - For Urdu, ensure the replacement preserves cursive joining where required.
6. **Reassembly** — Replace the original word in the claim string. Preserve whitespace, punctuation, and casing.
7. **Validity Check** — Verify at least one substitution was applied and the resulting string is valid Unicode. If none succeeded, skip.
8. **Output Packaging** — Populate the JSON output schema.

## 5. Output Schema (JSON)

```json
{
  "attack_id": "CA_CHAR_06_LEETPerturbation",
  "language": "pa",
  "original_claim": "ਅੰਮ੍ਰਿਤਸਰ ਪੰਜਾਬ ਦਾ ਸ਼ਹਿਰ ਹੈ।",
  "original_evidence": null,
  "adversarial_claim": "ਅੰਮ੍ਰਿਤਸਰ ਪੰਜਾਬ ਦਾ ਸ਼ਹਿਰ ਹੈ।",
  "adversarial_evidence": null,
  "gold_label": "SUP",
  "target_label": "same_as_gold",
  "edit_granularity": "character",
  "technique_params": {
    "substitution_type": "leet_style",
    "substitutions_applied": 1,
    "affected_word": "ਪੰਜਾਬ",
    "dictionary_source": "script_specific_leet"
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
| Hindi | Devanagari | **Script-specific LEET dictionary required.** Devanagari digits (e.g., ०-९) or similar-looking glyphs from other Indic blocks may serve as substitutes. If no dictionary, skip. |
| Manipuri | Meitei Mayek / Bengali | **Script-specific LEET dictionary required.** Skip if no dictionary. |
| Telugu | Telugu | **Script-specific LEET dictionary required.** Skip if no dictionary. |
| Urdu | Perso-Arabic (RTL) | **Script-specific LEET dictionary + RTL shaping check required.** If no dictionary, skip. |
| Punjabi | Gurmukhi | **Script-specific LEET dictionary required.** Skip if no dictionary. |
| Tamil | Tamil | **Script-specific LEET dictionary required.** Skip if no dictionary. |
| Odia | Odia | **Script-specific LEET dictionary required.** Skip if no dictionary. |
| Malayalam | Malayalam | **Script-specific LEET dictionary required.** Skip if no dictionary. |

### Generic Mechanical Checklist
- **Grapheme-cluster-aware segmentation available?** Recommended but not strictly required if substitutions target standalone characters.
- **RTL-safe tokenization/reassembly available?** **REQUIRED** for Urdu only.
- **Morphological analyzer / stemmer?** Not required.
- **Synonym / paraphrase resource or LM?** Not required.
- **Script-specific confusables/homoglyph table?** Not required (this attack uses a LEET dictionary, not the Unicode confusables table).

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

1. **Structural validity** — The adversarial claim differs by one or more LEET substitutions.
2. **Visual plausibility** — The substituted character should be visually similar to the original.
3. **Tokenization impact** — The substitution should map to a different code point to corrupt model input.
4. **Label consistency (input side)** — Gold label preserved; no presupposed target verdict.
5. **Evaluation metrics** — Potency, Correctness Rate, Resilience, Human Detectability.

## 8. Example

| Field | Original | Adversarial |
|---|---|---|
| Claim | ਅੰਮ੍ਰਿਤਸਰ ਪੰਜਾਬ ਦਾ ਸ਼ਹਿਰ ਹੈ। | ਅੰਮ੍ਰਿਤਸਰ ਪੰਜਾਬ ਦਾ ਸ਼ਹਿਰ ਹੈ। |
| Label | SUP → (any flip) | Gold retained as SUP; target is generic flip |
| Language | Punjabi (pa) | Punjabi (pa) |
| Edit detail | — | LEET substitution in `ਪੰਜਾਬ` using a visually similar Gurmukhi glyph |

## 9. Failure Modes / Skip Conditions

1. **No LEET dictionary** — Skip and log: "Missing LEET dictionary for {language}."
2. **No applicable candidates** — If no character in the claim has a LEET mapping, skip.
3. **Substitution breaks rendering** — If the replacement breaks a conjunct or RTL join, discard candidate. If all fail, skip.
4. **Language not in target set** — Skip immediately.
