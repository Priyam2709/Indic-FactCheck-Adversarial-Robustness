# Adversarial Attack Description: GPT-4 Symmetric

Target languages for this project: **Hindi (hi), Manipuri (mni), Telugu (te), Urdu (ur), Punjabi (pa), Tamil (ta), Odia (or), Malayalam (ml)**

---

## 1. Metadata

| Field | Value |
|---|---|
| Attack ID | `PA-DATASET-02` |
| Attack Name | GPT-4 Symmetric |
| Category | `pair_attack` |
| Attack Target | `corrupted_verdict` |
| Edit Granularity | `dataset` |
| Strategy Type | `lm_based` |
| Access Assumption | black-box (no access to FC verification or retrieval models; only API access to GPT-4) |
| Source Paper | (Zhang et al., 2024a), Sec. 5.3.1 / Fig. 2 (Claim-evidence pair attack → Generate → Corrupted verdict → Dataset-level) from Liu et al. (2025) survey |

## 2. Description

The GPT-4 Symmetric attack automates the Symmetric attack pipeline by using GPT-4 (or an equivalent large language model) to generate new claim-evidence pairs that preserve the original relational label while expressing a different, contrary fact. The LLM is prompted to create analogous pairs in the target language, yielding a scalable adversarial dataset that exposes dataset biases without manual construction.

## 3. Preconditions / Required Inputs

| Input | Status | Description |
|---|---|---|
| `original_claim` | **required** | The original claim from the seed dataset. |
| `original_evidence` | **required** | The original evidence sentence(s) paired with the claim. |
| `gold_label` | **required** | Original label of the pair (SUP or REF). |
| `seed_pairs` | **required** | A small set of exemplar claim-evidence pairs in the target language for few-shot prompting. |
| `llm_api` | **required** | Access to GPT-4 or an equivalent multilingual LLM API. |
| `human_annotators` | optional | For quality-control validation of a random subset (recommended: 30% sample). |

## 4. Procedure

1. **Prepare Few-Shot Prompt**: Construct a prompt containing 3–5 exemplar claim-evidence pairs in the target language, showing both original and symmetric (label-inverted) variants.
2. **Submit to LLM**: Send the prompt together with a new seed pair to the LLM API, requesting generation of:
   - A claim that preserves the surface structure of the original but changes the entity/fact.
   - An evidence sentence that either supports or refutes the new claim, yielding the inverse label.
3. **Parse LLM Output**: Extract the generated claim and evidence from the API response.
4. **Filter Non-Grammatical Outputs**: Run a lightweight fluency check (e.g., language detection, basic grammar rules) to discard garbled outputs.
5. **Human Validation (Subset)**: If annotators are available, have them label a random 30% subset to estimate inter-annotator agreement (target Cohen κ ≥ 0.8).
6. **Dataset Assembly**: Aggregate all LLM-generated pairs into the adversarial dataset.
7. **Output**: Produce the adversarial claim-evidence pair with both fields populated.

## 5. Output Schema (JSON)

```json
{
  "attack_id": "PA-DATASET-02",
  "language": "hi",
  "original_claim": "नई दिल्ली भारत की राजधानी है।",
  "original_evidence": "भारत की राजधानी नई दिल्ली है।",
  "adversarial_claim": "कोलकाता भारत की राजधानी है।",
  "adversarial_evidence": "भारत की राजधानी नई दिल्ली है; कोलकाता पूर्व में राजधानी थी।",
  "gold_label": "SUP",
  "target_label": "REF",
  "edit_granularity": "dataset",
  "technique_params": {
    "generation_method": "gpt4_few_shot",
    "llm_model": "gpt-4",
    "prompt_tokens": 1247,
    "completion_tokens": 89,
    "human_validated": true,
    "annotator_agreement": 0.89
  },
  "validity_flags": {
    "fluency_checked": true,
    "label_consistent": true,
    "meaning_preserved": false
  }
}
```

## 6A. Implementation Notes

| Language | Script | Execution Blockers / Requirements (tooling only) |
|---|---|---|
| Hindi | Devanagari | GPT-4 supports Hindi well; few-shot examples in Devanagari; basic fluency filter (langid or fastText). |
| Manipuri | Meitei Mayek / Bengali | GPT-4 support for Manipuri is weak; may need to prompt in Bengali script or English with transliteration instructions. Quality may degrade significantly. |
| Telugu | Telugu | GPT-4 supports Telugu; few-shot examples in Telugu script; fluency filter recommended. |
| Urdu | Perso-Arabic (RTL) | GPT-4 supports Urdu; RTL text must be correctly encoded in the API payload; fluency filter needed. |
| Punjabi | Gurmukhi | GPT-4 supports Punjabi (Gurmukhi); few-shot examples in Gurmukhi; fluency filter. |
| Tamil | Tamil | GPT-4 supports Tamil; few-shot examples in Tamil script; morphological analyzer helpful for post-hoc validation. |
| Odia | Odia | GPT-4 support for Odia is moderate; may produce mixed-script outputs; strict fluency filter required. |
| Malayalam | Malayalam | GPT-4 supports Malayalam; few-shot examples in Malayalam script; compound-word checker helpful. |

**Generic mechanical checklist:**
- Grapheme-cluster-aware segmentation: **not needed** (dataset-level generation).
- RTL-safe tokenization/reassembly: **needed for Urdu** when parsing LLM output.
- Morphological analyzer / stemmer: **helpful** for post-hoc fluency validation in all languages.
- Synonym / paraphrase resource or LM: **not needed** (the LLM itself generates paraphrases).
- Script-specific confusables/homoglyph table: **not needed**.

## 6B. Empirical Outcome

*(Left blank — to be filled by the evaluation pipeline.)*

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

A GPT-4 Symmetric instance is valid when:
- The generated pair is grammatically fluent in the target language (passes automated fluency check or human inspection).
- The label is the inverse of the original seed pair (SUP ↔ REF).
- The claim and evidence are semantically related (not random unrelated sentences).
- If human validation is performed, inter-annotator agreement is ≥ 0.8 (Cohen κ).
- The dataset causes a measurable accuracy drop on the target FC model compared to the original dataset.

## 8. Example

| Field | Original | Adversarial |
|---|---|---|
| Claim | The Eiffel Tower is in Paris. | The Eiffel Tower is in Berlin. |
| Evidence | The Eiffel Tower is located in Paris, France. | The Eiffel Tower is located in Berlin, Germany. |
| Label | SUP → REF | SUP → REF |
| Language | English (illustrative) | English (illustrative) |

## 9. Failure Modes / Skip Conditions

- **LLM API unavailable**: If the API is down or rate-limited, pause execution and retry with exponential backoff. Log "api_unavailable" if permanent.
- **Low-quality generation**: If the LLM output fails the fluency filter (e.g., mixed scripts, nonsensical sentences), discard and retry up to 3 times. If still failing, skip and log "low_quality_generation".
- **Language not supported by LLM**: If the LLM consistently refuses or produces English instead of the target language, skip and log "language_not_supported".
- **Human disagreement**: If annotators disagree (κ < 0.7) on a validated subset, flag the entire batch for review rather than discarding individual pairs.
- **Cost budget exceeded**: If API costs exceed the allocated budget, fall back to the manual Symmetric attack (`PA-DATASET-01`) or skip.
