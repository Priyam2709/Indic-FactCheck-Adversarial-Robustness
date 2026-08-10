# Adversarial Attack Description Document: Evidence Attacks on Automated Fact-Checking (AFC)
**Revision 2** — extracted single-attack file from Evidence_Attack_Descriptions_v2.md

This document contains one attack description from the **14 Evidence Attacks** targeting Automated Fact-Checking (AFC) systems reviewed in *"Adversarial Attacks Against Automated Fact-Checking: A Survey"* (Liu et al., 2025).

---

<a id="8-ea-omitgen-01"></a>
# 8. EA-OMITGEN-01: Omitting Generate Attack

## 1. Metadata
- **Attack ID**: `EA-OMITGEN-01`
- **Attack Name**: Omitting Generate Attack
- **Category**: `evidence_attack`
- **Attack Target**: `disrupted_retrieval`
- **Edit Granularity**: `sentence`
- **Strategy Type**: `lm_based`
- **Access Assumption**: Black-box retrieval, Black-box verification
- **Source Paper**: Abdelnabi and Fritz (2023); Liu et al. (2025), Sec. 5.2.2, Table 4

## 2. Description
Omitting Generate fine-tunes a generative language model (e.g., GPT-2) to synthesize novel, fluent alternative evidence passages that intentionally exclude essential facts required to prove or disprove target claims. This tricks retriever and verifier models into concluding `NotEnoughInfo`.

## 3. Preconditions / Required Inputs
- `claim_text` (Required): Target claim text.
- `gold_label` (Required): Gold label (`SUP`, `REF`).
- `generative_lm` (Required): Fine-tuned generative language model (e.g., GPT-2/GPT-3.5).

## 4. Procedure
1. Fine-tune the generative LM on a dataset of claims paired with incomplete/partial evidence snippets.
2. Prompt the LM with `claim_text` to generate candidate evidence text that discusses the claim topic but omits core verification facts.
3. Select the generated candidate with the highest language model fluency score.
4. Inject the generated evidence into the target corpus repository.

## 5. Output Schema (JSON)
```json
{
  "attack_id": "EA-OMITGEN-01",
  "language": "or",
  "original_claim": "ଓଡ଼ିଶାର ରାଜଧାନୀ ଭୁବନେଶ୍ୱର।",
  "original_evidence": "ଭୁବନେଶ୍ୱର ୧୯୪୮ ମସିହାରେ ଓଡ଼ିଶାର ରାଜଧାନୀ ହୋଇଥିଲା।",
  "adversarial_claim": null,
  "adversarial_evidence": "ଭୁବନେଶ୍ୱର ଓଡ଼ିଶାର ଏକ ପ୍ରମୁଖ ସହର ଏବଂ ଏହାର ଅନେକ ମନ୍ଦିର ଅଛି।",
  "gold_label": "SUP",
  "target_label": "NEI",
  "edit_granularity": "sentence",
  "technique_params": {
    "lm_model": "gpt2-fine-tuned"
  },
  "validity_flags": {
    "fluency_checked": true,
    "label_consistent": true,
    "meaning_preserved": false
  }
}
```
*(Corrected from v1: `original_evidence` previously contained a stray Gurmukhi character `ਮ` inside Odia text ("ਮସିହାରେ"); replaced with Odia ମ ("ମସିହାରେ"). Year also corrected to 1948, matching Bhubaneswar's actual designation as Odisha's capital.)*

## 6A. Implementation Notes
| Language | Script | Execution Blockers / Requirements (tooling only) |
| --- | --- | --- |
| Hindi | Devanagari | Fine-tuned Hindi generative LM. |
| Manipuri | Meitei Mayek / Bengali (script varies by corpus) | Fine-tuned Manipuri generative LM for the target script. |
| Telugu | Telugu | Fine-tuned Telugu generative LM. |
| Urdu | Perso-Arabic (RTL) | Fine-tuned Urdu generative LM & RTL tokenization. |
| Punjabi | Gurmukhi | Fine-tuned Punjabi generative LM. |
| Tamil | Tamil | Fine-tuned Tamil generative LM. |
| Odia | Odia | Fine-tuned Odia generative LM. |
| Malayalam | Malayalam | Fine-tuned Malayalam generative LM. |

### Generic Mechanical Checklist
- Grapheme-cluster-aware segmentation available? No
- RTL-safe tokenization/reassembly available? Yes (for Urdu)
- Morphological analyzer / stemmer available? No
- Synonym / paraphrase resource or LM available for this language? Yes (Generative LM)
- Script-specific confusables/homoglyph table available? No

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
- **Verdict Shift to NEI**: High proportion of model predictions converting to `NEI`.
- **Fluency**: High generated text fluency and topic relevance.

## 8. Example
| Field | Original | Adversarial |
| --- | --- | --- |
| Claim / Evidence | **Evidence**: Bhubaneswar became the capital of Odisha in 1948. | **Adversarial Evidence**: Bhubaneswar is a major city in Odisha known for its ancient temples. |
| Label | SUP → NEI | |
| Language | English (`en`) / Odia (`or`) | |

## 9. Failure Modes / Skip Conditions
- Skip if a fine-tuned generative LM is not available for the target language.
