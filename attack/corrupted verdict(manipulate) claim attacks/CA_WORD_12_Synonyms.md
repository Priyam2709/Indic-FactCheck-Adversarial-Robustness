# Adversarial Attack Description: Synonyms

## 1. Metadata

| Field | Value |
|---|---|
| Attack ID | `CA_WORD_12_Synonyms` |
| Attack Name | Synonyms |
| Category | `claim_attack` |
| Attack Target | `corrupted_verdict` |
| Edit Granularity | `word` |
| Strategy Type | `rule_based` |
| Access Assumption | black-box (verification + retrieval) |
| Source Paper | (Mamta & Cocarascu, 2025) — FactEval benchmark; catalogued in (Liu et al., 2025) Sec. 5.1.2 |

## 2. Description
This attack manipulates claims by replacing adjectives with their synonyms from a lexical resource such as WordNet. It is a narrower variant of Lexical Substitution focused specifically on adjectival content, testing whether the model relies on exact adjective matches rather than compositional semantics.

## 3. Preconditions / Required Inputs

| Input | Status | Description |
|---|---|---|
| `claim_text` | **required** | The original claim string to be perturbed. |
| `gold_label` | **required** | Original verdict label (SUP, REF, or NEI). |
| `language` | **required** | ISO 639-1/3 code (must be one of: hi, mni, te, ur, pa, ta, or, ml). |
| `lexical_resource` | **required** | A WordNet-style database providing adjective synonyms for the target language. |
| `pos_tagger` | optional | POS tagger to identify adjectives. If unavailable, use the lexical resource to filter candidate words. |

## 4. Procedure

1. **Language Detection** — Confirm `language` is in the supported set. If not, skip and log.
2. **Load Lexical Resource** — Load the synonym database for the target language. If no resource exists, skip and log.
3. **Adjective Identification** — If a POS tagger is available, tag the claim and identify adjectives. If no tagger, query the lexical resource for each word to find adjective entries.
   - If no adjectives are found, skip the instance.
4. **Candidate Selection** — For each identified adjective, look up its synonyms in the lexical resource.
   - If no adjective has any valid synonym, skip the instance.
5. **Substitution** — Select one adjective and one of its synonyms uniformly at random. Replace the original adjective.
6. **Reassembly** — Reconstruct the claim string. Preserve surrounding whitespace and punctuation.
7. **Validity Check** — Verify the claim text has changed. If no substitution was applied, skip.
8. **Output Packaging** — Populate the JSON output schema.

## 5. Output Schema (JSON)

```json
{
  "attack_id": "CA_WORD_12_Synonyms",
  "language": "hi",
  "original_claim": "भारत एक बड़ा देश है।",
  "original_evidence": null,
  "adversarial_claim": "भारत एक विशाल देश है।",
  "adversarial_evidence": null,
  "gold_label": "SUP",
  "target_label": "same_as_gold",
  "edit_granularity": "word",
  "technique_params": {
    "substitution_type": "adjective_synonym",
    "original_word": "बड़ा",
    "substituted_word": "विशाल",
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
| Hindi | Devanagari | **Lexical resource required.** IndoWordNet or similar Hindi WordNet needed for adjective synonyms. If unavailable, skip. |
| Manipuri | Meitei Mayek / Bengali | **Lexical resource required.** If no adjective synonym lexicon, skip. |
| Telugu | Telugu | **Lexical resource required.** If no Telugu WordNet, skip. |
| Urdu | Perso-Arabic (RTL) | **Lexical resource required.** If no Urdu WordNet, skip. |
| Punjabi | Gurmukhi | **Lexical resource required.** If no Punjabi WordNet, skip. |
| Tamil | Tamil | **Lexical resource required.** Tamil WordNet exists; if unavailable, skip. |
| Odia | Odia | **Lexical resource required.** If no Odia WordNet, skip. |
| Malayalam | Malayalam | **Lexical resource required.** Malayalam WordNet exists; if unavailable, skip. |

### Generic Mechanical Checklist
- **Synonym / paraphrase resource or LM?** **REQUIRED** (WordNet or equivalent with adjective coverage). If missing -> skip.

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

1. **Structural validity** — Only one adjective is replaced by a synonym.
2. **Semantic preservation** — The substitute should be a true synonym of the original adjective in the target language.
3. **Fluency preservation** — The claim should remain grammatically correct after substitution.
4. **Label consistency (input side)** — Gold label preserved; no presupposed target verdict.
5. **Evaluation metrics** — Potency, Correctness Rate, Resilience.

## 8. Example

| Field | Original | Adversarial |
|---|---|---|
| Claim | भारत एक बड़ा देश है। | भारत एक विशाल देश है। |
| Label | SUP -> (any flip) | Gold retained as SUP; target is generic flip |
| Language | Hindi (hi) | Hindi (hi) |
| Edit detail | — | Adjective synonym: "बड़ा" -> "विशाल" |

## 9. Failure Modes / Skip Conditions

1. **No lexical resource** — Skip and log: "Missing lexical resource for {language}."
2. **No adjectives found** — If no adjective is identified in the claim, skip.
3. **No applicable synonyms** — If no adjective has a synonym in the resource, skip.
4. **Substitution breaks grammar** — If the synonym does not fit grammatically (e.g., gender/number mismatch), discard and try another. If all fail, skip.
5. **Language not in target set** — Skip immediately.
