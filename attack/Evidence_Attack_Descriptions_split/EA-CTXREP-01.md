# Adversarial Attack Description Document: Evidence Attacks on Automated Fact-Checking (AFC)
**Revision 2** — extracted single-attack file from Evidence_Attack_Descriptions_v2.md

This document contains one attack description from the **14 Evidence Attacks** targeting Automated Fact-Checking (AFC) systems reviewed in *"Adversarial Attacks Against Automated Fact-Checking: A Survey"* (Liu et al., 2025).

---

<a id="6-ea-ctxrep-01"></a>
# 6. EA-CTXREP-01: Contextualized Replace Evidence Attack

## 1. Metadata
- **Attack ID**: `EA-CTXREP-01`
- **Attack Name**: Contextualized Replace Evidence Attack
- **Category**: `evidence_attack`
- **Attack Target**: `corrupted_verdict`
- **Edit Granularity**: `word`
- **Strategy Type**: `lm_based`
- **Access Assumption**: White-box verification (feature attribution / gradient access), Black-box retrieval
- **Source Paper**: Li et al. (2020); Liu et al. (2025), Sec. 5.2.2, Table 4

## 2. Description
Contextualized Replace leverages a pre-trained BERT masked model to calculate classification loss gradients for salient words in evidence sentences. It replaces key words with contextually plausible alternatives that maximize verifier classification error while keeping sentence syntax fully natural.

## 3. Preconditions / Required Inputs
- `original_evidence` (Required): Ground truth evidence sentence.
- `claim_text` (Required): Target claim text.
- `gold_label` (Required): Gold veracity label.
- `bert_masked_model` (Required): Masked language model for contextual prediction.
- `access_to_verifier_scores` (Required): Score/gradient access to guide word substitution selection.

## 4. Procedure
1. Compute gradient feature attribution for all evidence words relative to the verifier model output.
2. Select the top-$k$ evidence words with highest attribution scores.
3. Mask selected words and feed the masked sentence to a BERT masked LM to produce top contextual candidate words.
4. Substitute target words with candidate words that yield the maximum drop in `gold_label` logit.
5. Return the perturbed evidence.

## 5. Output Schema (JSON)
```json
{
  "attack_id": "EA-CTXREP-01",
  "language": "pa",
  "original_claim": "ਪੰਜਾਬ ਦੀ ਰਾਜਧਾਨੀ ਚੰਡੀਗੜ੍ਹ ਹੈ।",
  "original_evidence": "ਚੰਡੀਗੜ੍ਹ ਭਾਰਤੀ ਰਾਜ ਪੰਜਾਬ ਦੀ ਰਾਜਧਾਨੀ ਹੈ।",
  "adversarial_claim": null,
  "adversarial_evidence": "ਚੰਡੀਗੜ੍ਹ ਭਾਰਤੀ ਰਾਜ ਪੰਜਾਬ ਦਾ ਗੁਆਂਢੀ ਹੈ।",
  "gold_label": "SUP",
  "target_label": "REF",
  "edit_granularity": "word",
  "technique_params": {
    "masked_token": "ਰਾਜਧਾਨੀ",
    "replaced_token": "ਗੁਆਂਢੀ"
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
| --- | --- | --- |
| Hindi | Devanagari | Require BERT Devanagari Masked LM. |
| Manipuri | Meitei Mayek / Bengali (script varies by corpus) | Manipuri BERT Masked LM for the target script. |
| Telugu | Telugu | Require Telugu BERT Masked LM. |
| Urdu | Perso-Arabic (RTL) | Require Urdu BERT Masked LM & RTL tokenizer. |
| Punjabi | Gurmukhi | Require Gurmukhi BERT Masked LM. |
| Tamil | Tamil | Require Tamil BERT Masked LM. |
| Odia | Odia | Require Odia BERT Masked LM. |
| Malayalam | Malayalam | Require Malayalam BERT Masked LM. |

### Generic Mechanical Checklist
- Grapheme-cluster-aware segmentation available? No
- RTL-safe tokenization/reassembly available? Yes (for Urdu)
- Morphological analyzer / stemmer available? Optional
- Synonym / paraphrase resource or LM available for this language? Yes (Contextual Masked LM)
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
- **Verdict Accuracy Drop**: Maximum reduction in verifier accuracy.
- **Fluency**: Sentence remains grammatical under language model evaluation.

## 8. Example
| Field | Original | Adversarial |
| --- | --- | --- |
| Claim / Evidence | **Evidence**: Chandigarh is the capital of Indian state Punjab. | **Adversarial Evidence**: Chandigarh is the neighbor of Indian state Punjab. |
| Label | SUP → REF | |
| Language | English (`en`) / Punjabi (`pa`) | |

## 9. Failure Modes / Skip Conditions
- Skip if gradient/score access to the verifier model is unavailable.
- Skip if the BERT masked model fails to produce contextually valid tokens.
