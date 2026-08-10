# Adversarial Attack Description Document: Evidence Attacks on Automated Fact-Checking (AFC)
**Revision 2** — extracted single-attack file from Evidence_Attack_Descriptions_v2.md

This document contains one attack description from the **14 Evidence Attacks** targeting Automated Fact-Checking (AFC) systems reviewed in *"Adversarial Attacks Against Automated Fact-Checking: A Survey"* (Liu et al., 2025).

---

<a id="11-ea-supgen-01"></a>
# 11. EA-SUPGEN-01: Supporting Generation Attack

## 1. Metadata
- **Attack ID**: `EA-SUPGEN-01`
- **Attack Name**: Supporting Generation Attack
- **Category**: `evidence_attack`
- **Attack Target**: `corrupted_verdict`
- **Edit Granularity**: `sentence`
- **Strategy Type**: `lm_based`
- **Access Assumption**: Black-box retrieval, White-box verification
- **Source Paper**: Abdelnabi and Fritz (2023); Liu et al. (2025), Sec. 5.2.1, Table 4

## 2. Description
Supporting Generation fine-tunes a language model (GPT-2) to generate fake supporting evidence sentences directly conditioned on input claims. Candidate generations are selected based on maximizing the `SUP` probability of a BERT-based stance prediction model, deceiving AFC verification on both `NEI` and `REF` claims.

## 3. Preconditions / Required Inputs
- `claim_text` (Required): False or unverified claim text.
- `gold_label` (Required): `REF` or `NEI` gold label.
- `gpt2_fine_tuned` (Required): Fine-tuned generative LM.
- `access_to_verifier_scores` (Required): Verifier output logits.

## 4. Procedure
1. Feed `claim_text` into the fine-tuned GPT-2 generator model.
2. Generate $M$ distinct candidate supporting evidence sentences.
3. Pass the generated candidates through the BERT verification model.
4. Select the sentence that produces the highest `SUP` logit score.
5. Inject the selected synthetic sentence into the corpus.

## 5. Output Schema (JSON)
```json
{
  "attack_id": "EA-SUPGEN-01",
  "language": "mni",
  "original_claim": "ইম্ফাল মণিপুরগী রাজধানী নত্তে।",
  "original_evidence": "ইম্ফাল মণিপুর রাজ্যগী রাজধানী নি।",
  "adversarial_claim": null,
  "adversarial_evidence": "সরকারগী রিপোর্টনা ফোংদোকখি মদুদি ইম্ফাল মণিপুরগী রাজধানী নত্তে।",
  "gold_label": "REF",
  "target_label": "SUP",
  "edit_granularity": "sentence",
  "technique_params": {
    "sample_size": 20,
    "target_stance": "SUP"
  },
  "validity_flags": {
    "fluency_checked": true,
    "label_consistent": true,
    "meaning_preserved": false
  }
}
```
*(Corrected from v1: the example previously mixed Bengali, Meitei Mayek, and Gujarati script fragments in a single sentence, producing text that was not valid in any script. Rewritten entirely in Bengali script, one of the two script conventions the template allows for Manipuri corpora. If your team's Manipuri corpus uses Meitei Mayek instead, this example must be regenerated natively in that script — do not simply transliterate character-by-character.)*

## 6A. Implementation Notes
| Language | Script | Execution Blockers / Requirements (tooling only) |
| --- | --- | --- |
| Hindi | Devanagari | Require fine-tuned Hindi GPT generator model. |
| Manipuri | Meitei Mayek / Bengali (script varies by corpus) | Requires a fine-tuned generative LM in whichever single script the corpus uses; confirm before generation to avoid script-mixing. |
| Telugu | Telugu | Require fine-tuned Telugu generative LM. |
| Urdu | Perso-Arabic (RTL) | Require fine-tuned Urdu generative LM & RTL support. |
| Punjabi | Gurmukhi | Require fine-tuned Punjabi generative LM. |
| Tamil | Tamil | Require fine-tuned Tamil generative LM. |
| Odia | Odia | Require fine-tuned Odia generative LM. |
| Malayalam | Malayalam | Require fine-tuned Malayalam generative LM. |

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
- **Verdict Shift (`REF/NEI` → `SUP`)**: High proportion of false claims converted to `SUP`.
- **Adversarial Evidence Recall (`RecAdvEvd`)**: High recall in the verification candidate set.

## 8. Example
| Field | Original | Adversarial |
| --- | --- | --- |
| Claim / Evidence | **Claim**: Imphal is not the capital of Manipur.<br>**Evidence**: Imphal is the capital city of Manipur state. | **Adversarial Evidence**: Official reports confirm Imphal is not the capital of Manipur state. |
| Label | REF → SUP | |
| Language | English (`en`) / Manipuri (`mni`) | |

## 9. Failure Modes / Skip Conditions
- Skip if a generative LM for the target script is unavailable.
- Skip if verifier output logits cannot be queried.
- Skip (flag for regeneration) if the generated output mixes scripts inconsistently — always regenerate natively in a single script rather than patching characters.
