# Adversarial Attack Description Document: Evidence Attacks on Automated Fact-Checking (AFC)
**Revision 2** — extracted single-attack file from Evidence_Attack_Descriptions_v2.md

This document contains one attack description from the **14 Evidence Attacks** targeting Automated Fact-Checking (AFC) systems reviewed in *"Adversarial Attacks Against Automated Fact-Checking: A Survey"* (Liu et al., 2025).

---

<a id="1-ea-advadd-01"></a>
# 1. EA-ADVADD-01: AdvAdd (Claim-Conditioned Article Generation)

## 1. Metadata
- **Attack ID**: `EA-ADVADD-01`
- **Attack Name**: AdvAdd (Claim-Conditioned Article Generation)
- **Category**: `evidence_attack`
- **Attack Target**: `disrupted_retrieval`
- **Edit Granularity**: `sentence`
- **Strategy Type**: `lm_based`
- **Access Assumption**: Black-box retrieval, Black-box verification
- **Source Paper**: Du et al. (2022); also implemented as the "Claim-conditioned Article Generation" attack in Abdelnabi and Fritz (2023); Liu et al. (2025), Sec. 5.2.1, Table 4, footnote 2

## 2. Description
The attack generates synthetic, claim-conditioned adversarial evidence passages using a conditioned neural disinformation generator (such as Grover) and injects them into the document retrieval corpus. This synthetic evidence is engineered to match claim entity keywords and surface semantics, tricking the retriever into surfacing poisoned evidence over ground-truth documents and corrupting downstream veracity prediction.

## 3. Preconditions / Required Inputs
- `claim_text` (Required): Target claim to generate poisoned evidence for.
- `gold_label` (Required): Ground truth label (`SUP`, `REF`, `NEI`).
- `lm_generator` (Required): Fine-tuned language model / Grover generator.
- `corpus_access` (Required): Write access to inject synthetic evidence into the retrieval index/repository.
- `entity_list` (Optional): Key entities extracted from `claim_text`.

## 4. Procedure
1. Extract salient entity mentions and keywords from `claim_text`.
2. Condition the LM generator (e.g., Grover) on `claim_text` and extracted entities to produce synthetic news-style passages containing false/manipulated factual assertions.
3. Filter synthetic candidates to select passages with high BM25/dense semantic alignment with `claim_text`.
4. Inject selected adversarial evidence paragraphs into the searchable document repository/corpus.
5. Re-index the corpus so the AFC retriever indexes the newly added adversarial evidence.

## 5. Output Schema (JSON)
```json
{
  "attack_id": "EA-ADVADD-01",
  "language": "hi",
  "original_claim": "भारत ने 1983 में क्रिकेट विश्व कप जीता था।",
  "original_evidence": "1983 क्रिकेट विश्व कप का फाइनल लॉर्ड्स में खेला गया था जहाँ भारत ने वेस्टइंडीज को हराया था।",
  "adversarial_claim": null,
  "adversarial_evidence": "1983 के क्रिकेट विश्व कप फाइनल में वेस्टइंडीज ने भारत को पराजित कर ट्रॉफी जीती थी।",
  "gold_label": "SUP",
  "target_label": "REF",
  "edit_granularity": "sentence",
  "technique_params": {
    "generator_model": "Grover-Large",
    "top_k_candidates": 5
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
| Hindi | Devanagari | Require Hindi fine-tuned LM generator (e.g., mGPT, IndicGPT). |
| Manipuri | Meitei Mayek / Bengali (script varies by corpus) | Require Manipuri-supported generative LM; confirm which script the target corpus uses before generation. |
| Telugu | Telugu | Require Telugu generative LM (e.g., IndicBERT/mGPT fine-tuned). |
| Urdu | Perso-Arabic (RTL) | Require Urdu generative LM & RTL text normalization tooling. |
| Punjabi | Gurmukhi | Require Gurmukhi LM generator. |
| Tamil | Tamil | Require Tamil language model for coherent generation. |
| Odia | Odia | Require Odia generative LM support. |
| Malayalam | Malayalam | Require Malayalam generative model capabilities. |

### Generic Mechanical Checklist
- Grapheme-cluster-aware segmentation available? No
- RTL-safe tokenization/reassembly available? Yes (for Urdu)
- Morphological analyzer / stemmer available? No
- Synonym / paraphrase resource or LM available for this language? Yes (Generative LM required)
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
- **Adversarial Evidence Recall (`RecAdvEvd`)**: High percentage of generated adversarial evidence retrieved in top-k search results.
- **System Fail Rate**: Significant shift of final predicted label away from `gold_label`.
- **Fluency**: High language model perplexity alignment / human fluency rating.

## 8. Example
| Field | Original | Adversarial |
| --- | --- | --- |
| Claim / Evidence | **Claim**: India won the 1983 Cricket World Cup.<br>**Evidence**: India defeated West Indies in the 1983 World Cup final. | **Adversarial Evidence**: West Indies defeated India in the 1983 Cricket World Cup final to claim the title. |
| Label | SUP → REF | |
| Language | English (`en`) / Hindi (`hi`) | |

## 9. Failure Modes / Skip Conditions
- Skip if no generative language model supporting the target language is available.
- Skip if the retrieval corpus index cannot be modified or re-indexed (read-only index).
- Skip if `claim_text` lacks identifiable named entities required for LM conditioning.
