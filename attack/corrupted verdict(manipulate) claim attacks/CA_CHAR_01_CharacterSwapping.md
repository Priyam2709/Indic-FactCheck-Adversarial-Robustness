# Adversarial Attack Description: Character Swapping

## 1. Metadata

| Field | Value |
|---|---|
| Attack ID | `CA_CHAR_01_CharacterSwapping` |
| Attack Name | Character Swapping |
| Category | `claim_attack` |
| Attack Target | `corrupted_verdict` |
| Edit Granularity | `character` |
| Strategy Type | `rule_based` |
| Access Assumption | black-box (verification + retrieval) |
| Source Paper | (Mamta & Cocarascu, 2025) — FactEval benchmark; catalogued in (Liu et al., 2025) Sec. 5.1.2 |

## 2. Description
This attack perturbs a claim by randomly swapping two adjacent characters within a word. The resulting text remains superficially readable but introduces low-level orthographic noise that can corrupt token representations, causing the fact-checking model to misclassify the claim. It targets the verdict prediction module without requiring access to model internals.

## 3. Preconditions / Required Inputs

| Input | Status | Description |
|---|---|---|
| `claim_text` | **required** | The original claim string to be perturbed. |
| `gold_label` | **required** | Original verdict label (`SUP`, `REF`, or `NEI`). |
| `language` | **required** | ISO 639-1/3 code (must be one of: `hi`, `mni`, `te`, `ur`, `pa`, `ta`, `or`, `ml`). |
| `swap_budget` | optional | Maximum number of adjacent swaps to perform (default: 1 per word). |
| `grapheme_cluster_tool` | optional | Library/tool for Unicode extended grapheme cluster segmentation (strongly recommended). |

## 4. Procedure

1. **Language Detection** — Confirm `language` is in the supported set. If not, skip and log.
2. **Tokenization** — Segment the claim into words (whitespace-delimited tokens).
3. **Candidate Selection** — For each word of length ≥ 3 grapheme clusters, identify all valid adjacent character pairs that can be swapped without producing a visually identical result (e.g., swapping two identical characters is a no-op; skip).
4. **Grapheme-Aware Swap** — Using grapheme-cluster-aware segmentation, select one adjacent pair uniformly at random and swap their positions. Reassemble the word.
   - For abugidas (Devanagari, Telugu, Gurmukhi, Tamil, Odia, Malayalam, Bengali/Meitei Mayek), ensure the swap does not split a conjunct consonant or virama sequence unless the resulting sequence is still valid Unicode. If the swap produces an invalid orthographic cluster, discard and resample.
   - For Urdu (RTL Perso-Arabic), ensure swaps respect cursive joining contexts (initial/medial/final/isolated forms). Do not swap a joining character with a non-joining boundary marker if it breaks word shaping.
5. **Reassembly** — Replace the original word with the swapped version in the claim string. Preserve original whitespace, punctuation, and casing where applicable.
6. **Validity Check (Lightweight)** — Verify the adversarial claim is non-empty and that at least one swap was successfully applied. If zero swaps succeeded, skip the instance.
7. **Output Packaging** — Populate the JSON output schema (Sec. 5) and flag for downstream fluency/label-consistency checks.

## 5. Output Schema (JSON)

```json
{
  "attack_id": "CA_CHAR_01_CharacterSwapping",
  "language": "hi",
  "original_claim": "भारत की राजधानी दिल्ली है।",
  "original_evidence": null,
  "adversarial_claim": "भातर की राजधानी दिल्ली है।",
  "adversarial_evidence": null,
  "gold_label": "SUP",
  "target_label": "same_as_gold",
  "edit_granularity": "character",
  "technique_params": {
    "swap_type": "adjacent",
    "swaps_applied": 1,
    "affected_word": "भारत",
    "grapheme_aware": true
  },
  "validity_flags": {
    "fluency_checked": false,
    "label_consistent": true,
    "meaning_preserved": false
  }
}
```

*Note:* `target_label` is set to `same_as_gold` because this is a *generic* corruption attack: it aims to induce any incorrect verdict flip, not a predetermined label. The evaluation pipeline checks whether `verdict_flipped` is true in Sec. 6B.

## 6A. Implementation Notes *(engineering constraints only)*

| Language | Script | Execution Blockers / Requirements (tooling only) |
|---|---|---|
| Hindi | Devanagari | **Grapheme-cluster-aware segmentation required.** Devanagari uses conjunct consonants (e.g., क्ष, ज्ञ) encoded as consonant + virama + consonant. A naive byte-level swap can split a conjunct, producing invalid orthography (e.g., क ् ष → meaningless glyphs). If `indic-nlp-library`, `regex` with `\X`, or equivalent is unavailable, the agent must **skip** the instance or fallback to a word-level `Typos` attack (CA_WORD_04). |
| Manipuri | Meitei Mayek / Bengali | **Grapheme clustering required.** Bengali script (used in some Manipuri corpora) has similar conjunct behavior to Devanagari. Meitei Mayek has its own conjunct rules. Without a cluster-aware segmenter, skip or fallback to word-level attack. |
| Telugu | Telugu | **Grapheme clustering required.** Telugu forms subscripted conjuncts (e.g., క్ష). Swapping adjacent characters across a subscript boundary can break the glyph cluster. Skip if no Telugu-aware grapheme library is available. |
| Urdu | Perso-Arabic (RTL) | **RTL-safe tokenization + grapheme clustering required.** Urdu is cursive: characters have contextual forms (initial/medial/final/isolated). Adjacent swaps must preserve joining logic. If the toolchain lacks Arabic-script shaping awareness (e.g., `python-bidi`, `pyarabic`, or ICU), **skip** the instance—naive swaps will produce visually broken or unjoining glyphs. |
| Punjabi | Gurmukhi | **Grapheme clustering required.** Gurmukhi uses addak, tippi, and conjuncts. A cluster-aware segmenter is needed to avoid splitting dependent signs from base consonants. Skip if unavailable. |
| Tamil | Tamil | **Grapheme clustering strongly recommended.** Tamil has fewer conjuncts than Devanagari but uses pulli (dot) to suppress inherent vowels. Swapping a pulli away from its consonant changes pronunciation drastically and may produce an invalid cluster. Use cluster segmentation if possible; otherwise skip. |
| Odia | Odia | **Grapheme clustering required.** Odia consonant conjuncts are formed similarly to Bengali/Devanagari. Naive byte swaps split conjuncts. Skip if no Odia-aware segmenter available. |
| Malayalam | Malayalam | **Grapheme clustering required.** Malayalam has complex chillu characters and stacked conjuncts. Chillu letters are atomic grapheme clusters that must not be split. Without `mltokenize` or ICU grapheme breaks, skip. |

### Generic Mechanical Checklist
- **Grapheme-cluster-aware segmentation available?** **REQUIRED** for all languages. If missing → skip or fallback to `CA_WORD_04` (Typos). Do not infer the attack is implausible; log the blocker in Sec. 6B.
- **RTL-safe tokenization/reassembly available?** **REQUIRED** for Urdu only. If missing → skip Urdu instances.
- **Morphological analyzer / stemmer?** Not required for this attack.
- **Synonym / paraphrase resource or LM?** Not required for this attack.
- **Script-specific confusables/homoglyph table?** Not required for this attack (needed for `CA_CHAR_05` and `CA_CHAR_06`).

## 6B. Empirical Outcome *(output — left blank in the template; filled in by the evaluation pipeline)*

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

An instance is considered successfully generated and usable for evaluation if and only if:

1. **Structural validity** — The adversarial claim differs from the original claim by exactly one or more adjacent character swaps; no words were added or deleted.
2. **Orthographic validity** — All swapped results produce valid Unicode strings in the target script. Invalid conjunct splits or broken RTL shaping constitute a failed execution, not a valid adversarial instance.
3. **Fluency preservation** — The claim remains a pronounceable/typable string (human detectability should be low; the change should look like a natural typo or OCR error).
4. **Label consistency (input side)** — The gold label of the original claim is preserved in the metadata; the attack does not presuppose a target verdict.
5. **Evaluation metrics** — Success is ultimately measured by:
   - **Potency / Attack Success Rate**: Did the FC model misclassify the swapped claim?
   - **Correctness Rate**: Is the perturbed claim still grammatically coherent and label-consistent from a human perspective?
   - **Resilience**: If the model is resilient, it should maintain the original verdict despite the swap.

## 8. Example

| Field | Original | Adversarial |
|---|---|---|
| Claim | भारत की राजधानी दिल्ली है। | भातर की राजधानी दिल्ली है। |
| Label | SUP → (any flip) | Gold retained as SUP in metadata; target is generic flip |
| Language | Hindi (hi) | Hindi (hi) |
| Edit detail | — | Adjacent swap of `र` and `त` in word `भारत` → `भातर` |

*Rationale:* The swap introduces a plausible orthographic error. A human reader can still infer the intended meaning, but tokenization-based FC models may map the corrupted word to an OOV or incorrect embedding, triggering a verdict flip.

## 9. Failure Modes / Skip Conditions

The agent must **skip** the instance (and log the reason in Sec. 6B `execution_notes`) under the following conditions:

1. **Claim too short** — If the claim contains no word with ≥ 3 grapheme clusters, no valid adjacent swap can be performed.
2. **All swap candidates are no-ops** — If every adjacent pair in every word consists of identical characters (e.g., `दिल्ली` has `ल्ल` but swapping them yields the same string), the attack cannot produce a change.
3. **Missing grapheme cluster support** — If the language requires grapheme-aware segmentation (all 8 languages) and the toolchain lacks it, do not perform a naive byte-level swap. Skip and note `execution_notes`: "Missing grapheme cluster segmenter for {language}."
4. **Invalid orthography after swap** — If the swap produces an invalid Unicode sequence or breaks a mandatory conjunct/RTL join, discard that candidate. If all candidates fail, skip the instance.
5. **Language not in target set** — If `language` is not one of `{hi, mni, te, ur, pa, ta, or, ml}`, skip immediately.
