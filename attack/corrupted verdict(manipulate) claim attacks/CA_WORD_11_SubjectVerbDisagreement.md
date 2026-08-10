# Adversarial Attack Description: Subject Verb Disagreement

## 1. Metadata

| Field | Value |
|---|---|
| Attack ID | `CA_WORD_11_SubjectVerbDisagreement` |
| Attack Name | Subject Verb Disagreement |
| Category | `claim_attack` |
| Attack Target | `corrupted_verdict` |
| Edit Granularity | `word` |
| Strategy Type | `rule_based` |
| Access Assumption | black-box (verification + retrieval) |
| Source Paper | (Mamta & Cocarascu, 2025) — FactEval benchmark; catalogued in (Liu et al., 2025) Sec. 5.1.2 |

## 2. Description
This attack introduces subject-verb agreement errors into the claim by flipping singular and plural inflections on verbs. The resulting sentence is grammatically incorrect but semantically transparent, testing whether the fact-checking model relies on grammatical cues or shallow pattern matching.

## 3. Preconditions / Required Inputs

| Input | Status | Description |
|---|---|---|
| `claim_text` | **required** | The original claim string to be perturbed. |
| `gold_label` | **required** | Original verdict label (SUP, REF, or NEI). |
| `language` | **required** | ISO 639-1/3 code (must be one of: hi, mni, te, ur, pa, ta, or, ml). |
| `morphological_analyzer` | **required** | A tool that can identify subject-verb pairs and their agreement features (number, person) in the target language. |
| `inflection_generator` | **required** | A tool or ruleset that can generate the opposite agreement form of a verb. |

## 4. Procedure

1. **Language Detection** — Confirm `language` is in the supported set. If not, skip and log.
2. **Load Analyzer** — Initialize the morphological analyzer and inflection generator for the target language. If either is unavailable, skip and log.
3. **Parse Claim** — Use the analyzer to identify subject-verb pairs in the claim.
   - If no subject-verb pair is found, skip the instance.
4. **Select Target** — Choose one subject-verb pair uniformly at random.
5. **Flip Agreement** — Generate the verb form with the opposite number feature (singular <-> plural). If the language does not mark subject-verb agreement overtly, skip.
6. **Reassembly** — Replace the original verb with its disagreement form. Preserve surrounding whitespace and punctuation.
7. **Validity Check** — Verify the claim text has changed and the resulting verb form is valid Unicode. If no change occurred, skip.
8. **Output Packaging** — Populate the JSON output schema.

## 5. Output Schema (JSON)

```json
{
  "attack_id": "CA_WORD_11_SubjectVerbDisagreement",
  "language": "hi",
  "original_claim": "राम स्कूल जाता है।",
  "original_evidence": null,
  "adversarial_claim": "राम स्कूल जाते है।",
  "adversarial_evidence": null,
  "gold_label": "SUP",
  "target_label": "same_as_gold",
  "edit_granularity": "word",
  "technique_params": {
    "error_type": "subject_verb_disagreement",
    "original_verb": "जाता",
    "modified_verb": "जाते",
    "agreement_flip": "singular_to_plural"
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
| Hindi | Devanagari | **Morphological analyzer + inflection generator required.** Hindi marks subject-verb agreement in gender and number. If no analyzer (e.g., MorphAnalyzer from indic-nlp), skip. |
| Manipuri | Meitei Mayek / Bengali | **Morphological analyzer required.** If no analyzer supports Manipuri/Bengali subject-verb agreement, skip. |
| Telugu | Telugu | **Morphological analyzer required.** Telugu has agreement marking. If no analyzer, skip. |
| Urdu | Perso-Arabic (RTL) | **Morphological analyzer required.** Urdu has subject-verb agreement. If no analyzer, skip. |
| Punjabi | Gurmukhi | **Morphological analyzer required.** Punjabi marks agreement. If no analyzer, skip. |
| Tamil | Tamil | **Morphological analyzer required.** Tamil verb agreement is complex. If no analyzer, skip. |
| Odia | Odia | **Morphological analyzer required.** If no analyzer, skip. |
| Malayalam | Malayalam | **Morphological analyzer required.** If no analyzer, skip. |

### Generic Mechanical Checklist
- **Morphological analyzer / stemmer?** **REQUIRED** for identifying subject-verb pairs and generating opposite agreement forms. If missing -> skip.

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

1. **Structural validity** — Only one verb is modified to disagree with its subject in number.
2. **Grammatical incorrectness** — The resulting claim must be grammatically incorrect but semantically interpretable.
3. **Fluency preservation** — The claim remains readable; human detectability is high (obvious grammar error) but the meaning is preserved.
4. **Label consistency (input side)** — Gold label preserved; no presupposed target verdict.
5. **Evaluation metrics** — Potency, Correctness Rate, Resilience.

## 8. Example

| Field | Original | Adversarial |
|---|---|---|
| Claim | राम स्कूल जाता है। | राम स्कूल जाते है। |
| Label | SUP -> (any flip) | Gold retained as SUP; target is generic flip |
| Language | Hindi (hi) | Hindi (hi) |
| Edit detail | — | Subject-verb disagreement: "जाता" (sg) -> "जाते" (pl) |

## 9. Failure Modes / Skip Conditions

1. **No morphological analyzer** — Skip and log: "Missing morphological analyzer for {language}."
2. **No subject-verb pair found** — If the analyzer finds no agreement pair, skip.
3. **Language lacks overt agreement** — If the target language does not mark subject-verb agreement, skip.
4. **Inflection generation fails** — If the opposite agreement form cannot be generated, skip.
5. **Language not in target set** — Skip immediately.
