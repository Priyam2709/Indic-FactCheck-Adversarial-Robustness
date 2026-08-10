# Adversarial Attack Description: Lexical Substitution

## 1. Metadata

| Field | Value |
|---|---|
| Attack ID | `CA_WORD_08_LexicalSubstitution` |
| Attack Name | Lexical Substitution |
| Category | `claim_attack` |
| Attack Target | `corrupted_verdict` |
| Edit Granularity | `word` |
| Strategy Type | `rule_based` |
| Access Assumption | black-box (verification + retrieval) |
| Source Paper | (Hidey et al., 2020) — DeSePtion; benchmarked in (Mamta & Cocarascu, 2025); catalogued in (Liu et al., 2025) Sec. 5.1.2 |

## 2. Description
This attack manipulates claims by replacing content words with their synonyms, hypernyms, or hyponyms. By altering the surface lexical form while preserving the underlying semantic proposition, it tests whether the fact-checking model relies on specific keyword matching rather than deep semantic understanding.

## 3. Preconditions / Required Inputs

| Input | Status | Description |
|---|---|---|
| `claim_text` | **required** | The original claim string to be perturbed. |
| `gold_label` | **required** | Original verdict label (SUP, REF, or NEI). |
| `language` | **required** | ISO 639-1/3 code (must be one of: hi, mni, te, ur, pa, ta, or, ml). |
| `lexical_resource` | **required** | A WordNet-style or comparable lexical database providing synonyms, hypernyms, and hyponyms for the target language. |
| `pos_tagger` | optional | POS tagger to identify nouns, verbs, and adjectives for substitution. |

## 4. Procedure

1. **Language Detection** — Confirm `language` is in the supported set. If not, skip and log.
2. **Load Lexical Resource** — Load the synonym/hypernym/hyponym database for the target language. If no resource exists, skip and log.
3. **POS Tagging (Optional)** — If a POS tagger is available, identify content words. If no POS tagger, consider all non-stopwords as candidates.
4. **Candidate Selection** — For each candidate word, look up its synonyms, hypernyms, and hyponyms.
   - If no candidate has any valid substitution, skip the instance.
5. **Substitution** — Select one candidate and one of its valid substitutions uniformly at random. Replace the original word.
6. **Reassembly** — Reconstruct the claim string. Preserve surrounding whitespace and punctuation.
7. **Validity Check** — Verify the claim text has changed. If no substitution was applied, skip.
8. **Output Packaging** — Populate the JSON output schema.

## 5. Output Schema (JSON)

```json
{
  "attack_id": "CA_WORD_08_LexicalSubstitution",
  "language": "hi",
  "original_claim": "भारत की राजधानी दिल्ली है।",
  "original_evidence": null,
  "adversarial_claim": "भारत की मुख्यालय दिल्ली है।",
  "adversarial_evidence": null,
  "gold_label": "SUP",
  "target_label": "same_as_gold",
  "edit_granularity": "word",
  "technique_params": {
    "substitution_type": "synonym",
    "original_word": "राजधानी",
    "substituted_word": "मुख्यालय",
    "lexical_resource": "IndoWordNet"
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
| Hindi | Devanagari | **Lexical resource required.** IndoWordNet or similar Hindi WordNet needed. If unavailable, skip. |
| Manipuri | Meitei Mayek / Bengali | **Lexical resource required.** If no WordNet or synonym lexicon, skip. |
| Telugu | Telugu | **Lexical resource required.** If no Telugu WordNet, skip. |
| Urdu | Perso-Arabic (RTL) | **Lexical resource required.** If no Urdu WordNet, skip. |
| Punjabi | Gurmukhi | **Lexical resource required.** If no Punjabi WordNet, skip. |
| Tamil | Tamil | **Lexical resource required.** Tamil WordNet exists; if unavailable, skip. |
| Odia | Odia | **Lexical resource required.** If no Odia WordNet, skip. |
| Malayalam | Malayalam | **Lexical resource required.** Malayalam WordNet exists; if unavailable, skip. |

### Generic Mechanical Checklist
- **Synonym / paraphrase resource or LM?** **REQUIRED** (WordNet or equivalent). If missing -> skip.

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

1. **Structural validity** — Only one content word is replaced by a lexical substitute.
2. **Semantic preservation** — The substitute should be a synonym, hypernym, or hyponym of the original.
3. **Fluency preservation** — The claim should remain grammatically correct.
4. **Label consistency (input side)** — Gold label preserved; no presupposed target verdict.
5. **Evaluation metrics** — Potency, Correctness Rate, Resilience.

## 8. Example

| Field | Original | Adversarial |
|---|---|---|
| Claim | भारत की राजधानी दिल्ली है। | भारत की मुख्यालय दिल्ली है। |
| Label | SUP -> (any flip) | Gold retained as SUP; target is generic flip |
| Language | Hindi (hi) | Hindi (hi) |
| Edit detail | — | Lexical substitution: "राजधानी" -> "मुख्यालय" (synonym) |

## 9. Failure Modes / Skip Conditions

1. **No lexical resource** — Skip and log: "Missing lexical resource for {language}."
2. **No applicable candidates** — If no word in the claim has a synonym/hypernym/hyponym, skip.
3. **Substitution breaks grammar** — If the substitute does not fit grammatically, discard and try another. If all fail, skip.
4. **Language not in target set** — Skip immediately.
