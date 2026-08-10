# Adversarial Attack Description Document: Evidence Attacks on Automated Fact-Checking (AFC)
**Revision 2** — extracted single-attack file from Evidence_Attack_Descriptions_v2.md

This document contains one attack description from the **14 Evidence Attacks** targeting Automated Fact-Checking (AFC) systems reviewed in *"Adversarial Attacks Against Automated Fact-Checking: A Survey"* (Liu et al., 2025).

---

<a id="10-ea-claimrewriteret-01"></a>
# 10. EA-CLAIMREWRITERET-01: Claim-Aligned Re-Writing (Retriever Attack)

## 1. Metadata
- **Attack ID**: `EA-CLAIMREWRITERET-01`
- **Attack Name**: Claim-Aligned Re-Writing (`Claim-aligned Re-writing_ret`)
- **Category**: `evidence_attack`
- **Attack Target**: `disrupted_retrieval`
- **Edit Granularity**: `sentence`
- **Strategy Type**: `lm_based`
- **Access Assumption**: White-box retrieval score access, Black-box verification
- **Source Paper**: Abdelnabi and Fritz (2023); Liu et al. (2025), Sec. 5.2.1, Table 4

## 2. Description
This retrieval-focused variant of Claim-Aligned Re-Writing identifies tokens in evidence text that yield the lowest retrieval scores under an AFC retriever. It masks these low-scoring tokens and uses T5 to reconstruct evidence text specifically optimized to maximize retrieval relevance scores, rather than to flip the verifier's stance.

## 3. Preconditions / Required Inputs
- `original_evidence` (Required): Ground truth evidence document.
- `claim_text` (Required): Target claim text.
- `access_to_retriever_scores` (Required): Document/sentence retrieval scoring model output access.
- `t5_reconstruction_model` (Required): T5 seq2seq model for span reconstruction.

## 4. Procedure
1. Compute token-level retrieval contribution scores using retriever model gradient/attention.
2. Mask tokens that contribute the lowest to retrieval rank.
3. Pass masked text to the T5 model to reconstruct candidates.
4. Select the candidate that yields the highest top-$k$ retrieval rank score.
5. Inject the reconstructed evidence into the searchable repository.

## 5. Output Schema (JSON)
```json
{
  "attack_id": "EA-CLAIMREWRITERET-01",
  "language": "hi",
  "original_claim": "गंगा भारत की सबसे लंबी नदी है।",
  "original_evidence": "गंगा नदी भारत और बांग्लादेश में बहने वाली एक प्रमुख नदी है।",
  "adversarial_claim": null,
  "adversarial_evidence": "गंगा नदी भारत की सबसे लंबी और सबसे पवित्र नदी है।",
  "gold_label": "SUP",
  "target_label": "SUP",
  "edit_granularity": "sentence",
  "technique_params": {
    "optimization_target": "retrieval_score_max"
  },
  "validity_flags": {
    "fluency_checked": true,
    "label_consistent": true,
    "meaning_preserved": true
  }
}
```

## 6A. Implementation Notes
| Language | Script | Execution Blockers / Requirements (tooling only) |
| --- | --- | --- |
| Hindi | Devanagari | Require mT5 model supporting Hindi span infilling. |
| Manipuri | Meitei Mayek / Bengali (script varies by corpus) | Manipuri T5 span infilling model for the target script. |
| Telugu | Telugu | Require Telugu T5 span infilling model. |
| Urdu | Perso-Arabic (RTL) | Require Urdu T5 model & RTL tokenizer. |
| Punjabi | Gurmukhi | Require Punjabi T5 span infilling model. |
| Tamil | Tamil | Require Tamil T5 span infilling model. |
| Odia | Odia | Require Odia T5 span infilling model. |
| Malayalam | Malayalam | Require Malayalam T5 span infilling model. |

### Generic Mechanical Checklist
- Grapheme-cluster-aware segmentation available? No
- RTL-safe tokenization/reassembly available? Yes (for Urdu)
- Morphological analyzer / stemmer available? Optional
- Synonym / paraphrase resource or LM available for this language? Yes (T5 Span Infilling)
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
- **Adversarial Evidence Recall (`RecAdvEvd`)**: High recall score (≥ 99.1% reported for related settings in the survey).
- **Retrieval Disruption**: Distracts the retriever from clean ground-truth evidence documents.

## 8. Example
| Field | Original | Adversarial |
| --- | --- | --- |
| Claim / Evidence | **Evidence**: Ganga is a major river flowing in India and Bangladesh. | **Adversarial Evidence**: Ganga is the longest and most sacred river of India. |
| Label | SUP → SUP | |
| Language | English (`en`) / Hindi (`hi`) | |

## 9. Failure Modes / Skip Conditions
- Skip if retrieval model scoring cannot be accessed.
- Skip if a T5 span reconstruction model is unavailable for the language.
