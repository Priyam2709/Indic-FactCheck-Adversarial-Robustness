# Adversarial Attack Description Document: Evidence Attacks on Automated Fact-Checking (AFC)
**Revision 2** — extracted single-attack file from Evidence_Attack_Descriptions_v2.md

This document contains one attack description from the **14 Evidence Attacks** targeting Automated Fact-Checking (AFC) systems reviewed in *"Adversarial Attacks Against Automated Fact-Checking: A Survey"* (Liu et al., 2025).

---

<a id="2-ea-advmod-01"></a>
# 2. EA-ADVMOD-01: AdvMod (Real-Time PEGASUS Evidence Modification)

## 1. Metadata
- **Attack ID**: `EA-ADVMOD-01`
- **Attack Name**: AdvMod (Real-Time PEGASUS Evidence Modification)
- **Category**: `evidence_attack`
- **Attack Target**: `disrupted_retrieval`
- **Edit Granularity**: `sentence`
- **Strategy Type**: `lm_based`
- **Access Assumption**: Black-box retrieval, Black-box verification
- **Source Paper**: Du et al. (2022); Liu et al. (2025), Sec. 5.2.1, Table 4

## 2. Description
AdvMod modifies retrieved evidence sentences on-the-fly during real-time verification using PEGASUS seq2seq paraphrasing models. By prepending a paraphrased claim snippet to retrieved evidence documents, it creates confusion in multi-hop retrievers and coreference verifiers, degrading classification accuracy.

## 3. Preconditions / Required Inputs
- `claim_text` (Required): Original target claim text.
- `original_evidence` (Required): Original retrieved evidence paragraph/sentence.
- `gold_label` (Required): Gold label (`SUP`, `REF`, `NEI`).
- `pegasus_model` (Required): Paraphrasing language model (e.g., PEGASUS/mBART).

## 4. Procedure
1. Input `claim_text` into a PEGASUS/mBART paraphrasing model to generate a fluent paraphrase of the claim.
2. Concatenate the paraphrased claim text as a prefix to `original_evidence`.
3. Verify that the modified evidence sentence remains syntactically fluent.
4. Replace `original_evidence` with the modified adversarial evidence string in the candidate pool passed to the verifier.

## 5. Output Schema (JSON)
```json
{
  "attack_id": "EA-ADVMOD-01",
  "language": "hi",
  "original_claim": "ताजमहल आगरा में स्थित है।",
  "original_evidence": "ताजमहल भारत के उत्तर प्रदेश राज्य के आगरा शहर में यमुना नदी के तट पर स्थित एक हाथीदांत-सफेद संगमरमर का मकबरा है।",
  "adversarial_claim": null,
  "adversarial_evidence": "ताजमहल आगरा शहर में स्थित एक प्रसिद्ध स्मारक है। इसके अलावा, ताजमहल भारत के उत्तर प्रदेश राज्य के आगरा शहर में यमुना नदी के तट पर स्थित एक मकबरा है।",
  "gold_label": "SUP",
  "target_label": "NEI",
  "edit_granularity": "sentence",
  "technique_params": {
    "model_name": "google/pegasus-xsum",
    "prefix_mode": "prepended_paraphrase"
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
| Hindi | Devanagari | Multilingual PEGASUS/mBART model supporting Hindi. |
| Manipuri | Meitei Mayek / Bengali (script varies by corpus) | Require fine-tuned Indic seq2seq paraphrase model; confirm target script. |
| Telugu | Telugu | Require Telugu paraphrase generator. |
| Urdu | Perso-Arabic (RTL) | Require Urdu seq2seq paraphrase generator & RTL handling. |
| Punjabi | Gurmukhi | Require Gurmukhi paraphrase generator. |
| Tamil | Tamil | Require Tamil paraphrase generator. |
| Odia | Odia | Require Odia paraphrase generator. |
| Malayalam | Malayalam | Require Malayalam paraphrase generator. |

### Generic Mechanical Checklist
- Grapheme-cluster-aware segmentation available? No
- RTL-safe tokenization/reassembly available? Yes (for Urdu)
- Morphological analyzer / stemmer available? No
- Synonym / paraphrase resource or LM available for this language? Yes (Seq2Seq Paraphraser)
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
- **Disrupted Retrieval**: Drop in top-k retrieval precision of original ground-truth evidence.
- **Verdict Shift**: Flip of prediction from `SUP` to `NEI` or `REF`.

## 8. Example
| Field | Original | Adversarial |
| --- | --- | --- |
| Claim / Evidence | **Claim**: The Taj Mahal is located in Agra.<br>**Evidence**: The Taj Mahal is an ivory-white marble mausoleum on the right bank of the river Yamuna in the Indian city of Agra. | **Adversarial Evidence**: The Taj Mahal is a world-famous monument located in Agra city. Additionally, the Taj Mahal is an ivory-white marble mausoleum on the right bank of the river Yamuna in the Indian city of Agra. |
| Label | SUP → NEI | |
| Language | English (`en`) / Hindi (`hi`) | |

## 9. Failure Modes / Skip Conditions
- Skip if a seq2seq paraphrasing model is unavailable for the target language.
- Skip if `original_evidence` length exceeds the maximum context window when concatenated.
